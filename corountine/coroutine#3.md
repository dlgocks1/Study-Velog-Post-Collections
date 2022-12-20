# RunBlocking에 대해

```
runBlocking {
	// ...
}
```

> 새 코루틴을 실행하고 완료될 때까지 현재 스레드를 중단 없이 차단한다.

```
public actual fun <T> runBlocking(context: CoroutineContext, block: suspend CoroutineScope.() -> T): T {
```

**이 기능은 코루틴에서 사용해서는 안된다고 권장하고 있으며** suspend함수의 도메인 로직 테스트용으로만 쓰이도록 설계되었다.

사용되는 `CoroutineDispatcher`에서 해당 코루틴이 완료될 때 까지 block()내의 코드를 실행한다.

또한 컨텍스트를 지정할 수 있으며 지정할 수 있는 컨텍스트는 다음과 같다.
**어떤 스레드에서 코루틴을 돌릴지를 정의하는 것**

- Dispatcher.Main - 메인 스레드에서 동작(UI쓰레드)
- Dispatcher.IO - 네트워크 / 디스크(파일) 작업에 사용하는 방식
- Dispatcher.Default - CPU사용량이 많은 작업에 수행

코루틴이 중단되면(에러가 나거나, Thread.interrupt) `job`은 캔슬되고 코루틴은 `InterruptedException`을 발생시킨다.

- Job : 코루틴의 상태를 가지고 있으며 제어한다.
  Job은 하나의 CoroutineContext.Element이고, CoroutineScope.coroutineContext에는 반드시 Job이 포함되어 있어야만 한다.

## 실제 runBlocking 함수를 뜯어보자.

```
@Throws(InterruptedException::class)
public actual fun <T> runBlocking(context: CoroutineContext, block: suspend CoroutineScope.() -> T): T {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    val currentThread = Thread.currentThread()
    val contextInterceptor = context[ContinuationInterceptor]
    val eventLoop: EventLoop?
    val newContext: CoroutineContext
    if (contextInterceptor == null) {
        // create or use private event loop if no dispatcher is specified
        eventLoop = ThreadLocalEventLoop.eventLoop
        newContext = GlobalScope.newCoroutineContext(context + eventLoop)
    } else {
        // See if context's interceptor is an event loop that we shall use (to support TestContext)
        // or take an existing thread-local event loop if present to avoid blocking it (but don't create one)
        eventLoop = (contextInterceptor as? EventLoop)?.takeIf { it.shouldBeProcessedFromContext() }
            ?: ThreadLocalEventLoop.currentOrNull()
        newContext = GlobalScope.newCoroutineContext(context)
    }
    val coroutine = BlockingCoroutine<T>(newContext, currentThread, eventLoop)
    coroutine.start(CoroutineStart.DEFAULT, coroutine, block)
    return coroutine.joinBlocking()
}
```

위의 함수가 실행되며 어떤 일이 일어나는가?

---

### contract를 통한 컴파일러에게 실행횟수 전달

> Specifies that the function parameter lambda is invoked in place.

```
contract {
	callsInPlace(block, InvocationKind.EXACTLY_ONCE)
}
```

callsInPlace는 람다 함수를 사용할 때, 그 함수의 호출 횟수를 명시적으로 컴파일러에게 이해시켜주기 위해 사용
해당 block을 1번만 실행시킨다는 것을 컴파일러에게 전달

> 왜 전달해야 하는가?

```
fun main(){
    val str: String
    invokeLambda {
        str = "TEMP" // ERROR! 재할당 가능성으로 인해 캡처된 값 초기화가 금지되었습니다.
    }
}

fun invokeLambda(lambda: ()-> Unit){
    lambda()
}
```

블록으로 전달된 람다식을 1번만 실행할거라는 보장이 없기 때문에 setter을 한번밖에 할 수 없는 str은 오류를 발생하게 된다.

```
fun invokeLambda(lambda: ()-> Unit){
   // 해결!!
  contract {
        callsInPlace(lambda, InvocationKind.EXACTLY_ONCE)
    }
    lambda()
}
```

---

### 현재 쓰레드 가져와서 park 및 unpark 수행

```
    val currentThread = Thread.currentThread()
    // ...
    val coroutine = BlockingCoroutine<T>(newContext, currentThread, eventLoop)
    }
	coroutine.start(CoroutineStart.DEFAULT, coroutine, block)
    return coroutine.joinBlocking()
```

현재 쓰레드 상태를 가져온 후 해당 상태와 함께 `coroutine`을 생성하고 시작한다.

해당 코루틴은 `BlockingCoroutine`이며 생성자는 다음과 같다.

```
private class BlockingCoroutine<T>(
    parentContext: CoroutineContext,
    private val blockedThread: Thread,
    private val eventLoop: EventLoop?
) : AbstractCoroutine<T>(parentContext, true, true) {

 	// ...

 	override fun afterCompletion(state: Any?) {
        // wake up blocked thread
        if (Thread.currentThread() != blockedThread)
            unpark(blockedThread)
    }

}
```

joinBlocking() 함수가 Java의 LockSupport를 사용하여 현재 스레드를 파킹(차단)한다.
이후
afterCompletion()함수 내에서 파킹한 쓰레드에 대한 unpark를 진행하고 있다.

- park : 쓰레드를 잠구는 것 (남이 사용하지 못하게 재우는 것을 의미)
- unpark : 쓰레드를 깨우는 것 쓰레드를 사용할 수 있게 풀어줌

![](https://velog.velcdn.com/images/cksgodl/post/ee18fad0-077a-405d-9b72-f2428fff9d75/image.png)

이와 같이 runblocking을 실행할 때 Dispatcher의 쓰레드를 잠구는 것을 볼 수 있다.

---

### 자식의 job을 부모의 job에 합치기

`BlockingCoroutine`는 `AbstractCoroutine`를 상속받고 있다.

```
@InternalCoroutinesApi
public abstract class AbstractCoroutine<in T>(
    parentContext: CoroutineContext,
    initParentJob: Boolean,
    active: Boolean
) : JobSupport(active), Job, Continuation<T>, CoroutineScope {

    init {
        if (initParentJob) initParentJob(parentContext[Job])
    }
	// ...
}
```

1. coroutine이 생성될 때, `parentContext`를 인자로 받아온다.

2. parentContext에서 부모의 Job을 빼온다

```
initParentJob(parentContext[Job])
```

3. 자신의 job(자기 자신)을 부모의 child로 붙인다

```
val handle = parent.attachChild(this).
```

코루틴내에서 또 코루틴이 생성되면 이 job은 트리의 형태가 이루어지게 된다.

여기서 AbastractCoroutine 즉 `Coroutine`은 자기 자신이 CoroutineScope이며 Job이다.

- CoroutineScope - coroutine은 자기 자신이 scope가 되어 자신의 code block 안에서 자식 coroutine을 실행할 수 있다.
  또한, 자신의 coroutine context를 자식 coroutine에게 전달할 수 있다(e.g. 위에서 본 parentContext 주입 등).

### 이렇게 만들어지는 job tree 즉, coroutine트리의 구성을 알아보자.

launch, async, runblocking 등의 코루틴 런치함수에 코루틴 트리의 구성방법이 달라진다.

#### runBlocking의 예를보자.

```
 public actual fun <T> runBlocking(context: CoroutineContext, block: suspend CoroutineScope.() -> T): T {

    val eventLoop: EventLoop?
    val newContext: CoroutineContext
    if (contextInterceptor == null) {
        // 디스패처가 지정되지 않은 경우 개인 이벤트 루프 생성 또는 사용
        eventLoop = ThreadLocalEventLoop.eventLoop
        newContext = GlobalScope.newCoroutineContext(context + eventLoop)
    } else {
        newContext = GlobalScope.newCoroutineContext(context)
    }
    val coroutine = BlockingCoroutine<T>(newContext, currentThread, eventLoop)
    coroutine.start(CoroutineStart.DEFAULT, coroutine, block)
    return coroutine.joinBlocking()
}
```

runBlocking의 디스패쳐로 받아온 context를 활용해 `GlobalScope.newCoroutineContext`을 실행시켜 새로운 context를 사용하는 코루틴을 시작하고있다.

newCoroutineContext는 다음과 같이 실행된다.

```
@ExperimentalCoroutinesApi
public actual fun CoroutineScope.newCoroutineContext(context: CoroutineContext): CoroutineContext {
    val combined = foldCopies(coroutineContext, context, true)
    val debug = if (DEBUG) combined + CoroutineId(COROUTINE_ID.incrementAndGet()) else combined
    return if (combined !== Dispatchers.Default && combined[ContinuationInterceptor] == null)
        debug + Dispatchers.Default else debug
}
```

combined는 현재 CoroutineScope의 Context와 context param을 더해 반환하고 있다.

```
val combined = foldCopies(coroutineContext, context, true)
```

- coroutineContext는 GlobalScope의

> Job 트리에서 각 Job의 실행 순서는 어떻게 결정되는가? - 예를 들어 launch {}는 자신의 내부에서 실행된 coroutine의 종료를 기다리지 않는 반면, coroutineScope {}는 자신의 내부에서 실행된 coroutine이 모두 종료될 때까지 다음 코드를 실행하지 않는다. 둘의 동작 방식의 차이는 어디서 비롯되는가?

참고 자료 :

https://suhwan.dev/2022/01/21/Kotlin-coroutine-structured-concurrency/

https://suhwan.dev/2022/01/21/Kotlin-coroutine-structured-concurrency/

https://applefarm.tistory.com/124

https://velog.io/@l2hyunwoo/Kotlin-Coroutine-Basics

https://velog.io/@l2hyunwoo/Kotlin-Coroutine-Create-a-basic-coroutine

https://kotlinworld.com/380

https://maivve.tistory.com/3594
