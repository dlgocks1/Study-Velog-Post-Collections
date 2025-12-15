## 배경

코틀린 코루틴을 활용시에 `Continutation`을 스케줄링하는 스케줄러가 있다. 이를 `Dispatcher`라고 하며 통상적으로 `Dispatchers.IO`, `Dispatchers.Default`를 활용해 잡을 적절한 쓰레드로 할당시켜 작업을 수행한다.

`Dispatchers.IO`는 네트워크 작업과 같은 I/O작업이 있을 때 쓰이는 것을 권장하고 `Dispatchers.Default`는 CPU burst한 작업이 있을 때 쓰는 것을 권장한다.

하지만 무엇보다 급한작업이 있을 때 어떤 `Continuation`보다 가장 먼저 쓰레드에 할당되게 스케줄링하는 우선순위 기반 `Dispatcher`를 만들 수 있을까?

---

그전에 코루틴 및 디스패쳐에 대해 간단하게 알아보자.

![](https://velog.velcdn.com/images/cksgodl/post/e189c8d5-7182-4c00-9142-f3c0df3f6595/image.png)

[코루틴 디스패쳐 조금 더 살펴보기](
https://myungpyo.medium.com/%EC%BD%94%EB%A3%A8%ED%8B%B4-%EB%94%94%EC%8A%A4%ED%8C%A8%EC%B3%90-%EC%A1%B0%EA%B8%88-%EB%8D%94-%EC%82%B4%ED%8E%B4%EB%B3%B4%EA%B8%B0-92db58efca24)

> Worker은 자바 쓰레드를 의미한다.
>  IO 및 Default 디스패쳐는 동일한 쓰레드 풀을 공유한다.
>
내부에 Default, IO 디스패쳐의 경우 위 사진과 같이 `globalCpuQueue`, `globalBlockingQueue`에 나뉘어 적재되고 스케줄링된다. 
>
> 각 Worker는 내부에 `WorkQueue`를 기반으로 작업을 poll하여 작업하고, 각 워커끼리는 `Work stealing`알고리즘을 활용하여 작업을 분배한다.

자바 스레드는 운영체제 커널 스레드와 1대1 매칭된다.
따라서 JVM 어플리케이션 자체는 스레드 스케줄링에 관여하지 않고, OS가 관리한다.

## 구현 방향

조절할 수 있는 것은 2가지 정도가 있다.

1. 쓰레드 풀을 생성하고, OS가 해당 쓰레드를 우선적으로 스케줄링하게 한다. 
2. 쓰레드의 스케줄링 자체는 OS에 맡기고, 할당되는 `Task(Continuation)`에 우선순위를 적용하여 먼저 적재되게 한다.


### 1. 디스패쳐에서 활용하는 쓰레드 풀의 우선순위 높이기

OS 레벨에서 해당 스레드 자체의 우선순위를 높이는 방식을 활용할 수 있다. 코루틴 작업 스케줄링을 조절하는 것이 아니라, 해당 `Dispatcher`의 워커 스레드들이 CPU 시간을 더 많이 받도록 한다.

`Java Thread` 객체에는 Priority 기본옵션이 아래처럼 제공된다.
```kotlin
// Java Thread는 1~10 우선순위 지원
Thread.MIN_PRIORITY   // 1
Thread.NORM_PRIORITY  // 5 (기본값)
Thread.MAX_PRIORITY   // 10
```

따라서 높은 우선순위의 쓰레드풀을 가진 디스패쳐를 생성할 수 있다.

```kotlin
val highPriorityDispatcher = Executors.newFixedThreadPool(4) { runnable ->
    Thread(runnable, "HighPriority-${threadCount++}").apply {
        priority = Thread.MAX_PRIORITY  // 10
        isDaemon = true
    }
}.asCoroutineDispatcher()
```

물론 이는 생각처럼 작동하진 않는다. 그 이유로써는 OS단 쓰레드 우선순위를 어플리케이션이 잘 조절할 수 없음에 있다.

```sh
$ ps -eo pid,ni,comm | grep java
12345   0  java      ← nice 값 0 (기본)
```

일반 유저 프로세스는 nice 값을 낮출 수 없다. (우선순위 높이기 불가) 이런 명령을 위해서는 시스템 콜에 root권한 필요한데, 어플리케이션을 시작할 때 `sudo`권한으로 시작하기는 쉽지 않을것이다.

이런 권한없이 실행하면 JVM이 `pthread_setschedparam` 호출해도 권한 없으면 무시한다.

> **nice란? **
> 'nice' 값의 의미: 'niceness'는 해당 스레드가 다른 스레드에 대해 얼마나 "착하게(nice)" 행동하는지를 나타냅니다. 값이 높을수록 CPU 시간을 덜 요구하며, 이는 시스템에 더 '친절하다'는 의미입니다.
>
- 20: 가장 높은 우선순위
- 0: 기본값
- 19: 가장 낮은 우선순위

만약 작동한다고 해도 이는 JVM이 OS에 "이 스레드 중요해요"라고 알려주는 거지, 보장해주는 것은 아니다.


### 2. 할당되는 Task(Continuation)에 우선순위를 적용하여 먼저 적재되게 한다.

이를 위해서는 스케줄링 방식을 변경해야하고 이에 따라 커스텀 디스패쳐가 필요하다.

우선순위 기반 큐를 이용하고 코드로 구현하면 아래와 같다. 

```kotlin
// 우선순위 정의
enum class TaskPriority(val value: Int) {
    URGENT(0),
    HIGH(1),
    NORMAL(2),
    LOW(3)
}
```

코루틴 콘텍스트에 우선순위를 저장할 수 있도록 `AbstractCoroutineContextElement`을 상속받아 우선순위 구현체를 생성한다.


```kotlin
class PriorityElement(val priority: TaskPriority) : AbstractCoroutineContextElement(Key) {
    companion object Key : CoroutineContext.Key<PriorityElement>
}
```

우선순위 큐에서 꺼낼 `TaskWrapper` 클래스를 만든다. 기본적으로는 `Priority`에 의해 비교되며, 동일하다면 `sequence`를 통해 `FIFO`로 구현하도록 했다.

```kotlin
// PriorityQueue에 넣을 Task 래퍼
private class PrioritizedTask(
    val priority: Int,
    val sequence: Long,  // 같은 우선순위일 경우에는 FIFO 방식 활용
    val block: Runnable
) : Comparable<PrioritizedTask> {

    override fun compareTo(other: PrioritizedTask): Int {
        val cmp = priority.compareTo(other.priority)
        return if (cmp != 0) cmp else sequence.compareTo(other.sequence)
    }
}
```

이를 활용하여 커스텀 디스패쳐를 구현한다.

```kotlin
class PriorityDispatcher(
	// Default Dispatcher과 동일
    private val threadCount: Int = Runtime.getRuntime().availableProcessors()
) : CoroutineDispatcher(), AutoCloseable {

	// 우선순위 큐를 활용한다.
    private val queue = PriorityBlockingQueue<PrioritizedTask>()
    private val sequence = AtomicLong(0)

    @Volatile
    private var running = true

    private val workers = List(threadCount) { idx ->
        Thread {
            while (running) {
                try {
                    queue.poll(100, TimeUnit.MILLISECONDS)?.block?.run()
                } catch (e: InterruptedException) {
                    break
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
        }.apply {
            name = "PriorityWorker-$idx"
            isDaemon = true
            start()
        }
    }

    override fun dispatch(context: CoroutineContext, block: Runnable) {
        val priority = context[PriorityElement]?.priority ?: TaskPriority.NORMAL

        queue.offer(
            PrioritizedTask(
                priority = priority.value,
                sequence = sequence.getAndIncrement(),
                block = block
            )
        )
    }

    override fun close() {
        running = false
        workers.forEach { it.interrupt() }
    }
}

```

위처럼 작성한 디스패쳐는 동작은 하겠지만 몇가지 고려할 점이 있다. 

#### 문제점

1. 폴링이 CPU를 낭비한다.

이는 임의 구현체이기에 `while(true)`로 잡을 폴링하고 있지만 실제 구현체는 이렇게 작동하지 않는다.

```kotlin
// CoroutineScheduler.kt 에서 발췌/단순화
internal class CoroutineScheduler(
    private val corePoolSize: Int,
    private val maxPoolSize: Int
) : Executor, Closeable {
    
    // 글로벌 큐
    private val globalCpuQueue = GlobalQueue()
    private val globalBlockingQueue = GlobalQueue()
    
    // 워커들
    private val workers = AtomicReferenceArray<Worker?>(maxPoolSize + 1)
    
    inner class Worker private constructor() : Thread() {
        
        // 각 워커가 가진 로컬 큐 (work-stealing 대상)
        val localQueue = WorkQueue()
        
        // 워커 상태
        @Volatile
        var state = WorkerState.DORMANT
        
        private var park = Parker()  // LockSupport 기반
        
        override fun run() = runWorker()
        
        private fun runWorker() {
            while (!isTerminated) {
                val task = findTask()
                if (task != null) {
                    executeTask(task)
                } else {
                    park()  // 할 일 없으면 parking (CPU 안 씀)
                }
            }
        }
        
        private fun findTask(): Runnable? {
            // 1. 로컬 큐에서 먼저 찾기
            localQueue.poll()?.let { return it }
            
            // 2. 글로벌 큐에서 찾기
            globalCpuQueue.removeFirstOrNull()?.let { return it }
            
            // 3. 다른 워커 큐에서 훔치기 (work-stealing)
            return trySteal()
        }
        
        private fun trySteal(): Runnable? {
            val victim = workers.random()  // 실제론 더 정교함
            return victim?.localQueue?.steal()
        }
        
        private fun park() {
            state = WorkerState.PARKING
            // 핵심: busy-wait 아니고 OS 레벨 대기
            LockSupport.parkNanos(idleWorkerKeepAliveNs)
            state = WorkerState.DORMANT
        }
    }
    
    // 새 태스크 dispatch 시 워커 깨우기
    override fun execute(command: Runnable) {
        val task = TaskImpl(command)
        
        // 현재 스레드가 워커면 로컬 큐에
        val currentWorker = Thread.currentThread() as? Worker
        if (currentWorker != null) {
            currentWorker.localQueue.add(task)
        } else {
            globalCpuQueue.add(task)
        }
        
        // parking 중인 워커 깨우기
        signalWork()
    }
    
    private fun signalWork() {
        // 자고 있는 워커 찾아서 unpark
        for (i in 0 until workers.length()) {
            val worker = workers[i] ?: continue
            if (worker.state == WorkerState.PARKING) {
                LockSupport.unpark(worker)
                return
            }
        }
    }
}
```

실제 워커(쓰레드)는 할 일아 없으면 parking되어 CPU를 소비하지 않는다. 해당 로직을 추가해야 디스패쳐의 CPU 소비량을 줄일 수 있을 것이다.

2. 기아 상태가 발생한다.

높은 순위의 작업이 계속 추가되면 낮은 순위의 작업은 수행되지 않는다.

```kotlin
시간 →
─────────────────────────────────────────────────
URGENT 작업:  ■■■ ■■■ ■■■ ■■■ ■■■ ...  (계속 들어옴)
HIGH 작업:    대기... 대기... 대기...
LOW 작업:     대기... 대기... 영원히 대기...
```

따라서 `Aging` 기법을 도입해 오래 기다린 작업의 우선순위를 점점 높여주는 방식을 활용할 수 있다.

이는 OS 프로세스 스케줄링에서 활용되는 방법으로 이렇게 하면 오랫동안 기다린 프로세스가 결국에는 CPU를 할당받을 수 있다.

아니면 공정배분(fair share)기법을 활용할 수도 있다. 이또한 OS에서 활용되는 스케줄링 기법이다. 공정배분 스케줄러는 프로세스별로 CPU에 대한 지분을 나눠 배분하고, 각자의 지분에 맞게 자원을 할당해줘 작업을 처리시키는 스케줄러이다. (`예: URGENT 50%, HIGH 30%, NORMAL 15%, LOW 5%`)

## 결론

실제 우선순위 기반 커스텀 디스패쳐를 구현하기 위해서는 고려할 점이 많고, 이를 직접 해결하기엔 쉽지 않다.

- 적절한 Polling정책
- 기아(Starvation)상태 해결 
- 큐 경합 (Work-stealing 알고리즘 구현 등)

따라 실제 적용하기엔 쉽지 않고, 보통 대부분의 경우 아래와 같은 리소스 격리로 해결될 수 있다.

```kotlin
// 급한 작업: 별도 Dispatcher
val urgentScope = CoroutineScope(Dispatchers.IO.limitedParallelism(4))

// 일반 작업: Default 사용
val normalScope = CoroutineScope(Dispatchers.Default)
```

이는 특정 작업용으로 쓰레드 풀 4개를 격리한다. 이에 따라 일반 작업이 많아 쓰레드를 모두 사용하여도, 급한 작업용 쓰레드 4개는 격리되어 있어 Task 스케줄링이 분리된다.

이렇게 작업 후 스케줄링 자체는 OS에 맡기면 어느정도 우선순위가 할당된 디스패쳐를 활용할 수 있을 것이다.





