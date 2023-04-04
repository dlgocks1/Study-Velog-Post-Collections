## 소프트 레퍼런스와 가비지 컬렉터

자바의 참조 유형에는 크게 4가지가 있다.

1. Strong References (강한 참조)
2. Soft References (소프트 참조)
3. Weak References (약한 참조)
4. Phantom References (팬텀 참조)

### Strong References - 강한 참조

강한 참조란 기본 참조 유형을 의미한다.
`var strong: Referred? = Referred()`
해당 프로퍼티에 대한 참조를 가지고 있는 한 GC의 대상이 되지 않는다.

#### finalize 메서드??

자바의 최상위 클래스인 Object 클래스가 보유하고 있는 객체 소멸자 메소드를 의미한다. 리소스 누수(leak)를 방지하기 위해 자바 가상 머신(Java Virtual Machine)이 실행하는 가비지 컬렉션이 수행될 때 더 이상 사용하지 않는 자원에 대한 정리 작업을 진행하기 위해 호출되는 종료자 메서드이다.

```
class Referred {
    protected fun finalize() {
        println("객체 소멸자 호출")
    }
}

fun garbageCollect() {
    println("가비지 컬렉트 시작")
    System.gc()
    println("가비지 컬렉트 종료")
    Thread.sleep(5000)
}

fun main() {
    println("강한 참조 객체 만들기")
    var strong: Referred? = Referred()
    garbageCollect()
    println("레퍼런스 지우기")
    strong = null
    garbageCollect()
    println("종료")
}
```

![](https://velog.velcdn.com/images/cksgodl/post/10071fe0-85d6-4b9b-8900-5f696cca3390/image.png)

> `Strong References`는 해당 참조가 `null`이 되면 `GC`의 대상이 된다.

### Soft References (소프트 참조)

`Soft References`는 JVM에 메모리가 없을 경우 GC된다.
[Android Deloper - SoftReference](https://developer.android.com/reference/kotlin/java/lang/ref/SoftReference) 소프트 레퍼런스는 `OutOfMemoryError`를 실행하기 전에 지워지는 것이 보장된다. 하지만 강한 참조와 다르게 소프트레퍼런스는 지워지는 시간이나 순서에 제약 조건이 없다.(하지만 최근에 사용된 소프트 레퍼런스를 지우는 것으로 권장됨)

#### 캐싱에 소프트 참조를 사용하지 말 것

소프트 참조는 캐싱에 비효율 적이다. 런타임 때 삭제할 레퍼런스와 보관할 레퍼런스에 대한 공간이 충분하지 않기 때문이다. 또한 중요한 것 중 하나는 소프트 참조를 지울 것인지, 메모리 공간을 더 사용할 것인지 명확하지 않다는 것이다. 이러한 어플리케이션의 정보의 부족으로 인해 효율성이 제한되게 된다. 너무 일찍 삭제된 레퍼런스는 불필요한 작업을 유발하고, 늦게 삭제된 참조는 메모리는 낭비한다.

대부분의 응용 프로그램은 Android.util을 사용해야 한다. 소프트 참조 대신 `LruCache`를 사용할 수 있다. 이는 효율적인 캐시 정책이 있으며 사용자는 할당된 메모리의 양을 조정할 수 있다.

```
fun main() {
    println("약한 참조 객체 만들기")
    var strong: Referred? = Referred()
    val soft = SoftReference(strong)
    garbageCollect()
    strong = null
    garbageCollect()
    println(soft.get())
    println(strong)
    println("무제한 힙 생산")
    try {
        val heap: MutableList<Game> = ArrayList<Game>(100000)
        while (true) {
            heap.add(Game())
        }
    } catch (e: OutOfMemoryError) {
        println("OutOfMemory 발생")
    }
    println("종료")
}

```

![](https://velog.velcdn.com/images/cksgodl/post/b27d4b35-513b-46d7-90ba-f576975ee9a6/image.png)

```
소프트 참조 객체 만들기
가비지 컬렉트 시작
가비지 컬렉트 종료 // 정리되는 것 X
가비지 컬렉트 시작
가비지 컬렉트 종료 // Soft Reference로 설정하여 메모리가 부족할 때만 정리된다.
효율성.Referred@2d6e8792
null // 강한참조가 null이 되어도 소프트참조는 유지된다.
무제한 힙 생산
객체 소멸자 호출 // 메모리가 부족할 때 소프트참조 정리
OutOfMemory 발생
종료
```

### Weak References (약한 참조)

대상 객체를 참조하는 경우가 `WeakReferences` 객체만 존재하는 경우 GC의 대상이 된다.
다음 GC 실행시 무조건 힙 메모리에서 제거됩니다.

[Android Developer - WeakReference](https://developer.android.com/reference/kotlin/java/lang/ref/WeakReference) : 해당 참조가 소멸되고 소멸된 후 회수하는 것을 방지하지 않는다. `implement canonicalizing mappings`을 구현하는데 자주 사용된다.

```
fun main() {
    println("약한 참조 만들기")
    var strong: Referred? = Referred()
    val weak = WeakReference(strong)
    garbageCollect()
    println("참조 지우기")
    strong = null
    garbageCollect()
    println(strong)
    println(weak.get())
    println("종료")
}
```

![](https://velog.velcdn.com/images/cksgodl/post/0a2e018e-9509-4fca-a900-d694dc617ae9/image.png)

`strong = null` 소프트 참조와는 다르게, `WeakReferences`만 해당 프로퍼티를 참조하는 경우 GC의 대상이 되어 `null`이된다.

### Phantom References (팬텀 참조)

생성자에서 `ReferenceQueue`를 아규먼트로 받는다. GC가 실행되기 전에 (finalize()호출 후)
`PhantomReference`는 객체 내부의 참조를 `null`로 설정하지 않고 참조된 객체를 phantomly reachable 객체로 만든 이후에 `ReferenceQueue`에 enqueue 된다.

```
fun main() {
    println("팬텀 참조 생성")
    var ref: Game? = Game()
    val refQueue: ReferenceQueue<Game?> = ReferenceQueue<Game?>()
    val phantomRef: PhantomReference<Game> = PhantomReference<Game>(ref, refQueue)
    // 팬텀 참조는 아래처럼만 생성이 가능하다
    ref = null
    garbageCollect()
    println(phantomRef.isEnqueued)
    println(phantomRef.get())
    println("종료")
}
```

```
팬텀 참조 생성
가비지 컬렉트 시작
가비지 컬렉트 종료
true // phantomly reachable 객체로 큐에 삽입되어 있다.
null
```
