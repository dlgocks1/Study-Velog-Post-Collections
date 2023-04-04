[함수에 인라인 한정자 붙이기](https://velog.io/@cksgodl/Kotlin-%ED%95%A8%EC%88%98-%ED%83%80%EC%9E%85-%ED%8C%8C%EB%9D%BC%EB%AF%B8%ED%84%B0%EB%A5%BC-%EA%B0%96%EB%8A%94-%ED%95%A8%EC%88%98%EC%97%90-inline-%ED%95%9C%EC%A0%95%EC%9E%90%EB%A5%BC-%EB%B6%99%EC%9D%B4%EA%B8%B0)에서는 함수에 인라인을 붙였지만, **하나의 값을 보유하는 객체도 `inline`으로 만들 수 있다.**

> inline 클래스는 해당 객체를 사용하는 위치가 모두 해당 `프로퍼티`로 교체된다.

```
inline class Name(private val value: String) {

    // ...

    fun greet() {
        print("Hello, I am $value")
    }
}
```

이러한 `inline` 클래스는 타입만 맏다면, 다음과 같이 그냥 값을 곧바로 집어 넣는 것도 혀옹된다.

```
val name: Name = Name("해찬")
name.greet()
```

해당코드는 컴파일 시에 다음과 같은 코드로 변경된다.

```
// Kolin
val name: String = "해찬"
Name.`greet-impl`(name)

// Java
String name = Name.constructor-impl("해찬");
Name.greet-impl(name);
```

인라인 클래스는 다른 자료형을 래핑해서 새로운 자료형을 만들 때 많이 사용한다.(`String`을 `Name`으로 래핑하듯) 이때 어떠한 오버헤드도 발생하지 않는다.

`inline`클래스는 다음과 같은 상황에서 많이 사용된다.

> - 측정 단위를 표현할 때

- 타입 오용으로 발생하는 문제를 막을 때

## 측정 단위를 표현할 때

타이머 클래스를 만드는 경우를 가졍해보자. 특정 시간후 파라미터로 받은 함수를 호출한다.

```
interface Timer {
    fun callAfter(time: Int, callback: () -> Unit)
}
```

> 여기서 받은 `time`의 단위가 불명확하다. `ms`, `s`, `min` 중에서 어떤 단위인지 명확하지 않다.

가장 쉬운 방법은 파라미터 이름에 측정 단위를 붙여주는 것이다.

```
interface Timer {
    fun callAfter(timeMillis: Int, callback: () -> Unit)
}
```

하지만 함수를 사용할 때 이름있는 아규먼트를 사용하지 않으면 프로퍼티 이름이 표시되지 않을 수 있으므로, 여전히 실수를 할 수 있다.

```
callAfter(500) { // ms인지, s인지???
	// ...
}
```

또한 파라미터는 이름을 붙일 수 있지만, 리턴 값은 이름을 붙일 수 없다. 예를 들어 다음 코드의 `decideAboutTime`은 시간을 리턴하지만, 어떤 단위로 리턴하는지 전혀 알려 주지 않는다.

```
interface Timer {
    fun callAfter(timeMillis: Int, callback: () -> Unit)
}

interface User {
    fun decideAboutTime(): Int
    fun wakeUp()
}

fun setUpUserWakeUpUser(user: User, timer: Timer) {
    val time: Int = user.decideAboutTime()
    timer.callAfter(time) { // 언제 타이머가 작동될지 모름
        user.wakeUp()
    }
}
```

함수에 이름을 붙여서, 어떤 단위로 리턴하는지 알려 줄 수 있지만 (`decideAboutTimeMillis`로 만들면 `ms`단위를 반환함을 알 수 있다.) 이러한 해결 방법은 함수를 더 길게 만들고, 필요 없는 정보까지도 전달함으로 실제로는 거의 사용되지 않는다.

더 좋은 방법은 타입에 제한을 거는 것이다. 제한을 걸면 제네릭 유형을 잘못 사용하는 문제를 줄일 수 있다. 이때 코드를 더 효율적으로 만들고자 한다면, 다음과 같이 인라인 클래스를 활용한다.

```
interface Timer {
    fun callAfter(timeMillis: Minutes, callback: () -> Unit)
}

interface User {
    fun decideAboutTime(): Minutes
    fun wakeUp()
}

fun setUpUserWakeUpUser(user: User, timer: Timer) {
    val time: Minutes = user.decideAboutTime()
    timer.callAfter(time) { // 타입이 강제된다!
        user.wakeUp()
    }
}

inline class Minutes(val minutes: Int) {
    fun toMillis(): Millis = Millis(minutes * 60 * 1000)
}

inline class Millis(val milliseconds: Int) {
    // ..
}
```

타입이 `Minutes`로 강제된다.

![](https://velog.velcdn.com/images/cksgodl/post/fcd7e825-22df-48d7-b9ed-40b47de7086c/image.png)

프론트 개발 단위에서는 `px`, `mm`, `dp`등의 다양한 단위를 사용하는데, 이러한 단위를 제한할 때 활용하면 좋다. 또한 객체 생성을 위해 `DSL`과 같은 확장 프로퍼티를 만들어도 좋다.

```
val Int.min get() = Minutes(this)
val Int.ms get() = Millis(this)

val timeMin: Minutes = 10.min

```

## 타입 오용으로 발생하는 문제를 막자

`SQL` 데이터베이스는 일반적으로 `ID`를 활용하여 요소를 식별한다. `ID`값은 단순한 숫자임으로 혼동이 가능하기 때문에 이도 인라인 클래스를 활용하여 래핑할 수 있다.

```
inline class StudentId(val studenId: Int)
inline class TeacherId(val teacherId: Int)

@Entity(tableName = "grades")
class Grades(
    @ColumnInfo(name = "studentId")
    val studenId: StudentId,
    @ColumnInfo(name = "teacherId")
    val teacherId: TeacherId,
)
```

이렇게 하면 `ID`를 사용하는 것이 굉장히 안전해지며, 컴파일할 때 타입이 `Int`로 대체되고, 오버헤드도 발생하지 않는다.

## 인라인 클래스와 인터페이스

인라인 클래스도 다른 클래스와 마찬가지로 인터페이스를 구현할 수 있다.

```
interface TimeUnit {
    val millis: Long
}

inline class Minutes(val minutes: Long) : TimeUnit {
    override val millis: Long
        get() = minutes * 60 * 1000
}

inline class Millis(val milliseconds: Long) : TimeUnit {
    override val millis: Long
        get() = milliseconds

}

fun setUpTimer(time: TimeUnit) {
    val millis = time.millis
    // ...
}

fun main() {
    setUpTimer(Minutes(10))
    setUpTimer(Millis(60000))
}
```

`IDE`가 관련 정보를 제공해준다.
![](https://velog.velcdn.com/images/cksgodl/post/c2d9ae5d-9a12-4223-b3c0-8c837b9fac76/image.png)

하지만 이 코드는 클래스가 `inline`으로 동작하지 않는다. 따라서 위의 예는 클래스를 `inline`으로 만들었을 때 얻을 수 있는 장점이 하나도 없다. 인터페이스를 통해서 타입을 나타래며면, 객체를 래핑해서 사용해야 하기 때문이다.

```
public static final void main() {
	setUpTimer(Minutes.box-impl(Minutes.constructor-impl(10L)));
    setUpTimer(Millis.box-impl(Millis.constructor-impl(60000L)));
}
```

자바로 디컴파일을 해보면 `Minutes.box-impl(Minutes.constructor-impl(10L))` Minutes라는 객체를 생성(래핑)하고 있음을 볼 수 있다.

> 그러므로 인터페이스를 구현하는 인라인 클래스는 아무런 의미가 없다.

## typealias

`typealias`를 사용하면, 타입에 새로운 이름을 붙여 줄 수 있다.

```
typealias NewName = Int
val n: NewName = 10 // 가능!
```

이러한 typealias는 길고 반복적으로 사용해야 할 때 많이 유용하다. 예를 들어 다음과 같이 자주 사용되는 함수 타입은 `typealias`로 이름을 붙여서 사용한다.

`typealias`는 길고 반복적으로 사용해야 할 때 많이 유용하다.

```
typealias ClickListener = (view: View, event: Event) -> Unit

class View {
    fun addClickListener(listener: ClickListener) {}
    fun removeClickListener(listener: ClickListener) {}
    // ...
}
```

하지만 `typealias`는 장점도 있지만 단점도 있다.
다음의 예를 보자.

```
typealias Seconds = Int
typealias Millis = Int

fun getTime(): Millis = 10
fun setUpTimer(time: Millis) {}

fun main() {
    val seconds: Seconds = 10
    val millis: Millis = seconds // 컴파일 오류 발생 X
    setUpTimer(millis)

}
```

장점으로는 오버헤드가 전혀 발생하지 않는다는 것이다.

```
   public static final void setUpTimer(int time) {
   }

   public static final void main() {
      int seconds = 10;
      setUpTimer(seconds);
   }
```

자바로 디컴파일을 해보면 다른 추가 오브젝트가 생성되지 않음을 볼 수 있다.

하지만 단점도 존재한다.
`Seconds`와 `Millis`를 둘다 `Int`로 선언하여서 이를 혼용하여 사용하여도 에러가 발생하지 않는다. 오히려 `Millis`라고 이름이 명확하게 붙어 있음으로, 안전할 것이라는 착각을 하게 된다.

단위 등을 표현하려면 이름 또는 클래스를 사용하자. 이름은 비용이 적게 들고, 클래스는 안전하다.

> 인라인 클래스를 사용하면, 비용과 안전이라는 두마리 토끼를 모두 잡을 수 있다.

## 정리

인라인 클래스를 사용하면 성능적인 오버헤드 없이 타입을 래핑할 수 이다. 인라인 클래스는 타입 시스템을 통해 실수로 코드를 잘못 작성하는 것을 막아주므로, 코드의 안전성을 향상시킨다.

> 의미가 명확하지 않는타입, 여러 측정 단위가 섞여서 사용될 때 인라인 클래스를 꼭 활용하자.
