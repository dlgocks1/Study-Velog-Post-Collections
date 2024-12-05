
## 프로세스와 쓰레드
![](https://velog.velcdn.com/images/cksgodl/post/889c4dac-5f71-476d-ba49-97ac1fcb4a07/image.png)

> 프로세스란 실행중에 있는 프로그램을 의미한다.

디스크에 정적인 파일로 된 프로그램을 실행하면, 메모리 할당이 이루어지고, 할당된 메모리 공간으로 바이너리 코드가 올라가게 된다. 이 순간부터 프로세스라 불린다. 

프로세스 내부에는 최소 하나의 스레드를 가지고있고 여러 쓰레드를 통해 프로세스를 진행하는 것을 멀티스레드 프로그래밍이라고 한다. 

---

안드로이드에서는 `UI`를 수정하기 위한 작업은 메인스레드에서 진행되어야 한다.
5초이상의 시간동안 메인쓰레드가 작동하지 않으면 안드로이드는 `ANR`을 발생시켜 어플리케이션을 종료하게 된다.
따라서 사용자가 긴 작업을 수행할 때는 별도의 `쓰레드`나 `코루틴`에서 이를 작업하여야 한다.

## 멀티스레드는 어떻게 작동되는 것일까?

`CPU`는 한번에 하나의 스레드만 처리 가능하다. 위에서 말했던 멀티스레드란 동시에 여러 스레드를 동시에 실행하는 것이 아닌 안드로이드 OS `스케줄러`에 의해 스레드가 교체되면서 실행되는 것이다.

![](https://velog.velcdn.com/images/cksgodl/post/0a3b3bdd-8dc1-431e-bd62-08825f2b38af/image.png)

안드로이드 디밸로퍼에서는 멀티스레딩에 대해 다음과 같이 설명하고 있다.
> 멀티스레딩이란 동시에 여러 권의 책을 읽을 때 각 챕터 단위로 책을 번갈아 가며 읽는 것입니다. 
모든 책을 다 읽을 수 있지만 정확히 동시에 두 권 이상의 책을 읽을 수 없는 것과 같다고 생각할 수 있습니다.

### Context Switching이란?

이런 멀티스레딩을 구현하기 위해서 OS에서는 `문맥 교환` 즉 `Context Switching`을 이용하고 있다.

![](https://velog.velcdn.com/images/cksgodl/post/a220cfaf-5b9c-4bcb-9f44-a32e9583ffd8/image.png)

1. 프로세스 P0를 실행한다.
2. 프로세스 P1을 실행시키기 위해 인터럽트(시스템 콜)이 요청된다.
3. P0의 실행중인 상태를 PCB0에 저장한다. 
4. PCB1의 상태를 복구하여 레지스터에 넣는다.
5. 프로세스 P1를 실행한다.
6. 프로세스 P0을 실행시키기 위해 인터럽트(시스템 콜)이 요청된다.
이후 반복

PCB(Process Control Block)에는 다음과 같은 정보가 저장된다.
* PID : 프로세스의 고유 번호
* 상태 : 준비, 대기, 실행 등의 상태
* 포인터 : 다음 실행될 프로세스의 포인터 (레지스터 PC)
* Priority : 스케줄링 및 프로세스 우선순위
* 할당된 자원 정보 등등..

---

### Context Switching의 간단한 예제

```
val thread1 = Thread {
    Log.i("MainACtivity-Thraed-1", Thread.currentThread().name)
    for (i in 0..100) {
        println("$i")
    }
}
val thread2 = Thread {
    Log.i("MainACtivity-Thraed-2", Thread.currentThread().name)
    for (i in 100..200) {
        println("$i")
    }
}

thread1.start()
thread2.start()
```

![](https://velog.velcdn.com/images/cksgodl/post/ecea7fd5-6608-44e8-8640-17e9eed9ec78/image.png)

1부터 100까지 출력하는 `Thread1`과 100 부터 200까지 출력하는 `Thread2`의 콘텍스트 스위칭이 되며 돌아가는 결과를 확인할 수 있다.



## 스레드끼리의 통신 방법

멀티스레딩을 활용해 백그라운드에서 긴 작업을 수행한 결과를 어떻게 메인쓰레드에 전달하여 UI를 업데이트할 수 있을까?

안드로이드에서는 쓰레드간의 통신을 위해 `Looper`와 `Handler`를 제공해준다고 한다.

### Looper란?

하나의 쓰레드에는 하나의 `Looper`가 존재 가능하다. 메인 쓰레드에서는 실행됨과 동시에 `Looper`가 자동으로 생성된다. 

`Looper`내부에는 `MessageQueue`가 존재하고 해당 쓰레드가 처리해야할 동작이 큐에 하나씩 쌓이게 된다. 루퍼는 해당 큐에 들어오는 메시지들을 하나씩 꺼내어 `Handler`로 전달하는 역할을 수행한다.


### Handler란?

`Looper`의 `MessageQueue`에 메시지를 넣을수도 있고 `MessageQueue`에서 특정 메시지를 꺼내어 이를 처리하는 기능도 수행한다.


`Handler`의 내부 소스를 한번 살펴보자.


* 핸들러의 생성자
```
public Handler(@NonNull Looper looper) {
	this(looper, null, false);
}

@UnsupportedAppUsage
public Handler(@NonNull Looper looper, @Nullable Callback callback, boolean async) {
        mLooper = looper;
        mQueue = looper.mQueue;
        mCallback = callback;
        mAsynchronous = async;
}
```
1. `looper` -> 위에서 설명한 쓰레드의 루퍼를 의미한다.
2. `mQeue` -> 루퍼의 메시지 큐
3. `mAsynchronous` -> 비동기 실행을 가능하게 만드는 속성같은데 사용하는 방법을 찾지 못함


4. `mCallback` -> Callback함수를 상속받는 함수형 인터페이스
```
public interface Callback {
        boolean handleMessage(@NonNull Message msg);
}
```

### 동작 플로우

![](https://velog.velcdn.com/images/cksgodl/post/7458becc-f24c-4f28-8ea2-46c40eb88809/image.png)


1. `Thread2`에서 `Thread1`의 루퍼를 가진 `Handler`에게 `sendMessage()`를 요청하여 메시지를 전달한다.
2. `Thread1`의 루퍼는 `MessageQueue`에서 `loop()`를 통해 무한순환을 돌며 메시지를 하나씩 `Handler`에게 전달한다.
3. `Handler`에서 `handleMEssage()`를 통해 메시지를 처리한다.


### 실제 예시

이를 직접 백그라운드 쓰레드와 메인쓰레드에서 구현해보자.

1. 테스트를 위한 `TestThread`를 생성한다.
	메인쓰레드의 정보전달을 위한 `handler`를 인자로 받아오게 세팅

```
class TestThread(
    private val handler: Handler
) : Thread() {

    override fun run() {
        super.run()
        Log.i("TestThread : ", currentThread().name)

        for (i in 0..10) {
            handler.sendMessage(Message.obtain().apply {
                arg1 = i
            })
        }
    }
}
```

2. `MainActivity`에서의 쓰레드 실행

```
override fun onCreate(savedInstanceState: Bundle?) {

	val callback = object : Handler.Callback {
        override fun handleMessage(msg: Message): Boolean {
            btText.value = msg.arg1.toString()
            Log.i("Handler-Thread", Thread.currentThread().name)
            Log.i("Handler", msg.arg1.toString())
            return true
        }
    }

    val mainThreadHandler = Handler(Looper.getMainLooper(), callback)

    thread = TestThread(mainThreadHandler)
    thread.start()
}
```

> 루퍼를 따로 생성하지도 않고 loop()를 돌지도 않는데요??

위에서 말했듯이 `Main thread`는 초기 루퍼가 자동생성되어 `Looper.getMainLooper()`로 루퍼를 얻을 수 있으며 메인 스레드의 `Looper`는 앱 실행 중인 동안 무한 루프를 실행한다.

결과로는
![](https://velog.velcdn.com/images/cksgodl/post/6c718cec-6eed-4147-a56e-82770211d77f/image.png)

`ThestThread`는 `Thread-2`라는 쓰레드에서 동작하며,

![](https://velog.velcdn.com/images/cksgodl/post/052d583c-b442-4373-82f4-5d40874151d8/image.png)

메시지큐에 넣은 데이터들을 로그로 확인할 떄는 `main`쓰레드에서 처리가 가능함을 알 수 있다.
따라서 UI의 변경작업도 가능하다.

## Compose에서는 백그라운드 쓰레드에서의 UI업데이트가 자유롭다.


[Can Jetpack Compose draw/update UI from any thread?](https://stackoverflow.com/questions/68839242/can-jetpack-compose-draw-update-ui-from-any-thread)


안드로이드 디벨로퍼에서는 다음과 같이 설명하고 있다.

>**Composable 함수는 동시에 실행할 수 있음**
`Compose`는 `Composable`함수를 동시에 실행하여 `recomposition`을 최적화할 수 있습니다.
이 최적화는 `composable`함수가 백그라운드 스레드 풀 내에서 실행될 수 있음을 의미합니다. `Compose`는 동시에 여러 스레드에서 `composable`함수를 호출할 수 있습니다.


`compose`에서는 리컴포지션에 사용되는 `state`를 선언하고 이 `state`가 변경될 때 `recomposition`이 일어난다. 여러 스레드에서 해당 `state`를 참조하게 된다면 `thread safe`하지 않겠지만 이에 따라 `recomposition`은 일어날 것이며 뷰 업데이트는 가능할 것이다. 

따라서 `composable`함수를 다시 그리는 `recomposition`은 동시에 병렬로 실행될 수 있다. 즉 `recomposition`이 일어나는 도중에 `state`가 변하면 `Composable`은 진행중이던 `recomposition`을 건너뛴다.



>* 재구성은 최대한 많은 수의 구성 가능한 함수 및 람다를 건너뜁니다.
* 재구성은 낙관적이며 취소될 수 있습니다.
* 구성 가능한 함수는 애니메이션의 모든 프레임에서와 같은 빈도로 매우 자주 실행될 수 있습니다.

```
Row {
    Column {
        Button(onClick = {
            val thread = Thread {
                Log.i("MainACtivity-Thraed-1", Thread.currentThread().name)
                for (i in 0..100) {
                    Thread.sleep(1000)
                    text = i.toString()
                }
            }
            thread.start()
        }) {
            Text(text = "Start Thread_1")
        }
    }
    Button(onClick = {
        val thread = Thread {
            Log.i("MainACtivity-Thraed-2", Thread.currentThread().name)
            for (i in 100..200) {
                Thread.sleep(1000)
                text = i.toString()
            }
        }
        thread.start()
    }) {
        Text(text = "Start Thread_2")
    }
}
Text(text = text)
```

![](https://velog.velcdn.com/images/cksgodl/post/8209ff8b-c112-4f0f-976d-ca2b1d6669a0/image.gif)




## 메인쓰레드가 아닌 Thread와 Thread간의 통신 구현

`Thread2`를 클래스를 선언하고 해당 클래스의 핸들러를 멤버변수로 추출해준다. 
[Andorid developer - Looper](https://developer.android.com/reference/android/os/Looper) 참조 


```
class TestThread2() : Thread() {

    private val callback = Handler.Callback { msg ->
        Log.i("Handler-Thread2", currentThread().name)
        Log.i("Handler", msg.arg1.toString())
        true
    }
    var mHandler: Handler? = null

    override fun run() {
        super.run()
        Looper.prepare()
        mHandler = Handler(Looper.myLooper()!!, callback)
        Looper.loop()
    }
}
```

메인 스레드가 아닌 스레드는 기본 `Looper`를 생성하지 않는다. 따라서 `Looper.prepare()`를 활용하여 루퍼 및 메시지큐를 생성한 후 `mHanlder`멤버 변수에 해당 루퍼를 담은 멤버변수를 할당해주자.

`Looper.loop()`를 활용하여 무한 루프를 돌며 메시지큐를 확인한다.

`Thread1`에서는 인자로 받은 핸들러에 1부터 10까지의 메시지를 보낸다.
```
class TestThread1(
    private val handler: Handler
) : Thread() {

    override fun run() {
        super.run()
        for (i in 0..10) {
            handler.sendMessage(Message.obtain().apply {
                arg1 = i
            })
        }
    }
}
```

`Thread2`를 생성한 후  `Thread1`에 핸들러를 인자로 넣어 생성한다.

```
private lateinit var thread: TestThread1
private lateinit var thread2: TestThread2

// On Created
thread2 = TestThread2()
thread2.start()

if(thread2.mHandler != null) {
    thread = TestThread(thread2.mHandler!!)
	thread.start()
}
```

* 결과
```
I/TestThread1 : Thread-3
I/TestThread2 : Thread-2
```

![](https://velog.velcdn.com/images/cksgodl/post/633a62c7-c79e-4c60-9be7-1ff6a41ac2e2/image.png)

위의 예시에서는 `handler`에 `Message`객체를 전달하고 있지만, `Runnable`객체도 전달할 수 있다.

---

> `Runnable`이란??
Thread를 인터페이스화 한 형태라고 생각하면 된다. SAM로 구성되며 이런 단일 함수 인터페이스는 코틀린에서는 람다식으로 변환하여 간편하게 사용 가능하다.

`Thread`는 별도의 클래스를 만들어서 `start()`해야한다. `Thread` 클래스를 상속받으면 다른 클래스를 상속받을 수 없다.(단일 상속) 또한 `Thread` 클래스를 상속받으면 `Thread` 클래스에 구현된 코드를 활용할 수 있다.

* `Thread`에서는 `start`를 호출해야 한다. `run`을 직접 호출하는 것은 메인 쓰레드에서 객체의 메소드를 호출하는 것에 불과하다. 이를 별도의 쓰레드로 실행시키려면 JVM의 도움이 필요하다. 그러기 위해서는 `start()`를 호출해야 한다.

---

다음 예시는 핸들러를 활용하여 메시지큐에 `Runnable`과 `Message`를 전달하는 소스이다.

```
override fun run() {
    super.run()
    for (i in 0..10) {
        handler.sendMessage(Message.obtain().apply {
            arg1 = 100
        })
        handler.post {
		    Log.i("Runnable전달했음 : ", i.toString())
			sleep(1000L)
		}
    }
}
```

위의 반복문을 돌며 메시지큐에 넣는다면 다음과 같은 형태가 될 것 이다.
```
Message | Runnable | Message | Runnable | Message | Runnable | ...
```
여기서 예상과는 다른 타이밍 이슈가 발생할 수 있다. 메시지**`큐`**이기 때문에 `FIFO`으로 진행되고 `Runnable`객체는 `sleep(1000)`을 내부에 가지고 있기 때문에 한 메시지를 처리하는데 1초씩 걸리게 된다. 따라 10번 째 `Message`를 출력하는데 10초 이상의 시간이 걸리게 된다.

![](https://velog.velcdn.com/images/cksgodl/post/85f713dd-b4bf-4e95-9b70-d802d1e44f3e/image.png)

또한 메시지큐는 Activity의 생명주기 중`OnResume`이후에 실행되기에 원하는 시점과는 다른 타이밍에 실행될 수 있다

> 즉 메시지큐의 처리 시점은 보장할 수 없다.










## 참고 자료

https://developer.android.com/courses/extras/multithreading?hl=ko

https://stackoverflow.com/questions/68839242/can-jetpack-compose-draw-update-ui-from-any-thread

https://velog.io/@ho-taek/Android-%EC%8A%A4%EB%A0%88%EB%93%9C%EB%9E%80

https://devyul.tistory.com/entry/Android-%EC%8A%A4%EB%A0%88%EB%93%9CThread%EC%99%80-%ED%95%B8%EB%93%A4%EB%9F%ACHandler

