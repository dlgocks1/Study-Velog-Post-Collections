이번장에서 배울 것

- 클래스 및 인터페이스
- 중요하지 않은 프로퍼티와 생성자
- 데이터 클래스
- 객체 키워드 사용

## 4.1 클래스 계층구조 정의

이 섹션에서는 `Kotlin`에서 클래스 계층 구조가 어떻게 정의되는지 살펴본다. `Kotlin`의 가시성 및 액세스 수정자와 `Kotlin`이 선택하는 기본값을 살펴본다. 또한 클래스의 가능한 하위 클래스 또는 인터페이스 구현을 제한하는 `sealed` 클래스에 대해서도 알아본다.

### 4.1.1 Kotlin의 인터페이스

`Kotlin` 인터페이스는 추상 메서드의 정의와 비추상 메서드의 구현을 포함할 수 있지만 상태를 포함할 수는 없다.

`Kotlin`에서 인터페이스를 선언하려면 인터페이스 키워드를 사용한다. 버튼이나 하이퍼링크와 같이 클릭 가능한 요소임을 나타내는 예제이다.

```kotlin
interface Clickable {
    fun click()
}
```

이것은 값을 반환하지 않는 클릭이라는 단일 추상 메서드가 있는 인터페이스를 선언 한다. 인터페이스를 구현하는 모든 비추상 클래스는 이 메서드의 구현을 제공해야 한다.

```kotlin
class Button : Clickable {
    override fun click() = println("I was clicked")
}
fun main() {
    Button().click()
    // I was clicked
}
```

`Kotlin`은 클래스 이름 뒤에 콜론을 사용하여 구성(즉, 인터페이스 구현)과 상속(서브클래싱)을 모두 상속받을 수 있다. 클래스는 원하는 만큼 많은 인터페이스를 구현할 수 있지만 하나의 클래스만 확장할 수 있다.

오버라이드 수정자는 슈퍼클래스 또는 인터페이스의 메서드 및 프로퍼티를 재정의하는 메서드 및 프로퍼티를 재정의하는데 사용된다. 선택 사항인 `@override` 어노테이션을 사용하는 `Java`와 달리 `Kotlin`에서는 `override` 수정자를 사용하는것이 필수이다. 이렇게 하면 구현을 작성한 후에 메서드를 추가한 경우 실수로 메서드를 재정의하는 실수를 방지할 수 있으며, 메서드를 명시적으로 재정의로 표시하거나 이름을 바꾸지 않으면 코드가 컴파일되지 않는다.

인터페이스 메서드는 기본 구현을 가질 수 있다. 이렇게 하려면 메서드 본문을 프로비저닝하면 된다. 이 경우 `Clickable` 인터페이스에 단순히 텍스트를 프린트하는 기본 구현을 가진 함수 `showOff()`를 추가할 수 있다.

```kotlin
interface Focusable {
    fun setFocus(b: Boolean) =
        println("I ${if (b) "got" else "lost"} focus.")
    fun showOff() = println("I'm focusable!")
}
```

클래스에서 두 인터페이스를 모두 구현해야 한다면 어떻게 될까? 

> 동일한 멤버에 대한 구현이 두 개 이상 상속되는 경우 명시적인 구현을 제공해야 한다.

```kotlin
class Button : Clickable, Focusable {
    override fun click() = println("I was clicked")
	
    override fun showOff() {
    	super<Clickable>.showOff()
    	super<Focusable>.showOff()
	}
}
```

참고) `Kotlin`은 기본 메서드가 있는 각 인터페이스를 인터페이스 + 메서드 바디를 정적 메서드로 포함하는 클래스의 조합으로 컴파일한다. 인터페이스에는 선언만 포함되고 클래스에는 모든 구현이 정적 메서드로 구현된다. 따라서 `Java` 클래스에서 이러한 인터페이스를 구현해야 하는 경우 `Kotlin`에서 메서드 바디가 있는 메서드를 포함하여 모든 메서드의 구현을 직접 정의해야 한다. 

```kotlin
class JavaButton implements Clickable {
    @Override
    public void click() {
        System.out.println("I was clicked");
	}
    @Override
    public void showOff() {
        System.out.println("I'm showing off");
    }
}
```

### 4.1.2 open, final 및 abstract 수정자: 기본은 final

기본적으로 모든 클래스와 메서드는 기본적으로 최종 클래스이므로 `Kotlin`클래스에 대한 서브클래스를 만들거나 기본 클래스의 메서드를 재정의할 수 없다.

이는 모든 클래스의 서브클래스를 생성할 수 있고 `final`로 명시적으로 표시되지 않는 한 모든 메서드를 재정의할 수 있는 `Java`와 차별화된다. 하지만 왜 `Kotlin`은 이 접근 방식을 따르지 않았을까? 이 방식은 흔히 통용되지만 문제가 될 수 있기 때문이다.

소위 __취약한 기본 클래스 문제__는 기본 클래스의 변경된 코드가 더 이상 하위 클래스 의 가정과 일치하지 않아 기본 클래스를 수정하면 하위 클래스의 잘못된 동작이 발생할 수 있을 때 발생한다. 

클래스가 서브클래스를 어떻게 재정의해야 하는지(어떤 메서드를 어떻게 재정의해야 하는지)에 대한 정확한 규칙을 제공하지 않으면 클라이언트는 기본 클래스 작성자가 예상하지 못한 방식으로 메서드를 재정의할 수 있는 위험이 있다. 모든 서브클래스를 분석하는 것은 불가능하기 때문에 기본 클래스를 변경하면 서브 클래스의 동작이 예기치 않게 변경될 수 있다는 점에서 기본 클래스는 "취약하다"고 할 수 있다.

> "상속을 위해 설계하고 문서화하거나 그렇지 않으면 상속을 금지"해야 한다. 

`Kotlin`은 이 철학을 따르며 기본적으로 클래스, 메서드 및 프로퍼티를 `final`으로 만든다. 클래스의 서브클래스를 만들 수 있도록 하려면 클래스에 `open` 수정자를 표시해야 한다. 또한 재정의할 수 있는 모든 프로퍼티나 메서드에 `open` 수정자를 추가해야 한다.

단순한 버튼 이상으로 사용자 인터페이스를 멋지게 꾸미고 클릭 가능한 `RichButton`을 만들고 싶다고 가정해 보자. 이 클래스의 서브클래스는 자체 애니메이션을 제공할 수 있어야 하지만 버튼 비활성화 같은 기본 동작을 중단할 수 없어야 한다.

```kotlin
open class RichButton : Clickable {
    fun disable() { /* ... */ }
    open fun animate() { /* ... */ }
    override fun click() { /* ... */ }
}
```

```kotlin
class ThemedButton : RichButton() {
    override fun animate() { /* ... */ }
    override fun click() { /* ... */ }
    override fun showOff() { /* ... */ }
}
```

베이스 클래스나 인터페이스의 멤버를 재정의하면 재정의하는 멤버도 기본적으로 열려 있다는 점에 유의하자. 이를 변경하여 클래스의 서브클래스가 구현을 재정의하지 못 하도록 하려면 재정의된 멤버를 명시적으로 최종 멤버로 표시하면 된다.

```kotlin
open class RichButton : Clickable {
    final override fun click() { /* ... */ }
}
```

> `final`인 클래스의 중요한 이점 중 하나는 스마트형변환이 가능하다는 것이다. 컴파일러는 타입 검사 후 변경할 수 없는 변수에 대해서만 스마트 형변환(추가 수동 형변환 없이 멤버에 액세스할 수 있는 자동형변환)을 수행할 수 있다.
>
> 클래스의 경우, 이는 스마트 형변환은 값이고 사용자 정의 접근자가 없는 클래스 프로퍼티 에서만 사용할 수 있음을 의미한다. 그렇지 않으면 서브클래스가 프로퍼티를 재정의하고 커스텀 접근자를 정의하여 스마트 형변환의 핵심 요구 사항을 위반할 수 있기 때문에 이 요구 사항은 프로퍼티가 최종적이어야 함을 의미한다.

클래스를 추상 클래스로 선언하여 인스턴스화할 수 없도록 만들 수도 있다. 추상 클래스에는 일반적으로 구현이 없고 서브클래스에서 재정의해야 하는 추상 멤버가 포함된다. 추상 멤버는 항상 열려있으므로 인터페이스에 명시적 `open` 수정자를 사용할 필요가 없다.

추상 클래스의 예로는 `Animtead`의 속성을 정의하는 클래스가 있다. 애니메이션 속도와 프레임 수, 애니메이션 실행을 위한 동작과 같은 속성을 포함한다. 이러한 프로퍼티와 메서드는 다른 객체에 의해 구현 될 때만 의미가 있으므로 `Animated`는 추상적으로 표시된다.

```kotlin
abstract class Animated {
    abstract val animationSpeed: Double
    val keyframes: Int = 20
    open val frames: Int = 60
    abstract fun animate()
    open fun stopAnimating() { /* ... */ }
    fun animateTwice() { /* ... */ }
}
```

![](https://velog.velcdn.com/images/cksgodl/post/4b2ebf46-332f-4ef6-821c-22559fe71098/image.png)

### 4.1.3 공개 여부 수정자: 기본적으로 Pulbic

가시성 수정자는 코드베이스의 선언에 대한 액세스를 제어하는데 도움이 된다. 클래스의 구현 세부 사항의 표시 여부를 제한하면 클래스에 의존하는 코드가 손상될 위험 없이 변경할 수 있다.

`public` 선언은 모든곳에서 볼 수 있고, `protected` 선언은 하위클래스에서 볼 수 있으며, `private` 선언은 클래스내부에서만 볼 수 있다.

__`Kotlin`에서 기본값은 `public` 선언이다.__

> Kotlin에서 비공개 패키지 가시성 없음
>
> `Kotlin`에는 `Java`의 기본 가시성 기능인 패키지 비공개 가시성 개념이 없다. `Kotlin`은 네임스페이스에서 코드를 구성하는 방법으로만 패키지를 사용하며, 가시성 제어에는 패키지 를 사용하지 않는다.

`Kotlin`에서는 클래스, 함수 및 속성을 비롯한 최상위 선언에 비공개 표시를 사용할 수 있다. 이러한 선언은 해당 선언이 선언된 파일에서만 볼 수 있다. 

![](https://velog.velcdn.com/images/cksgodl/post/6a770e83-2e2a-4246-b356-2e301cbc52a4/image.png)

```kotlin
internal open class TalkativeButton {
    private fun yell() = println("Hey!")
    protected fun whisper() = println("Let's talk!")
}

fun TalkativeButton.giveSpeech() { // ERROR : publicmember exposes its internal receiver type TalkativeButton
    yell() // Error: Cannot access yell; it is private in TalkativeButton
	whisper()  // Error:publicmember exposes its internal receiver type TalkativeButton
}
```

`Java`와 `Kotlin`에서 `protected` 수정자에 대한 동작의 차이점에 유의하라. `Java`에서는 동일한 패키지에서 보호된 멤버에 액세스할 수 있지만 `Kotlin`에서는 이를 허용하지 않는다.

`Kotlin`에서는 표시 규칙이 간단하며 `protected` 멤버는 클래스와 그 하위 클래스에서만 볼 수 있다. 또한 클래스의 확장함수는 비공개 또는 보호된 멤버에 액세스할 수 없다.

> `Kotlin`에서 `Java` 바이트코드로 컴파일할 때 `Publice`, `Protected` 및 비공개 수정자가 보존된다. 이러한 `Kotlin` 선언은 `Java` 코드에서 동일한 가시성으로 선언된 것처럼 사용할 수 있다. 하지만, `Private`클래스는 다르. 이 클래스는 내부적으로 패키지 비공개 선언으로 컴파일된다(`Java`에서는 클래스를 비공개로 만들 수 없음).

`Kotlin`과 `Java`의 또 다른 가시성 규칙의 차이점은 `Kotlin`에서 외부 클래스는 내부(또는 중첩) 클래스의 비공개 멤버를 볼 수 없다는 것이다.  

헬퍼 클래스를 캡슐화하거나 코드를 사용되는 위치에 가깝게 유지하려는 경우 다른 클래스 내부에 클래스를 선언할 수 있다. 하지만 `Java`와 달리 `Kotlin`의 중첩 클래스는 특별히 요청하지 않는 한 외부 클래스 인스턴스에 액세스할 수 없다. 이것이 중요한 이유를 보여주는 예제를 살펴보겠다.

```kotlin
interface State : Serializable
interface View {
    fun getCurrentState(): State
    fun restoreState(state: State) { /* ... */ }
}
```

`Button` 클래스에서 버튼 상태를 저장하는 클래스를 정의한다. `Java`에서이를 수행하는 방법을 살자.

```kotlin
/* Java */
public class Button implements View {
    @Override
    public State getCurrentState() {
        return new ButtonState();
    }
    @Override
    public void restoreState(State state) { /*...*/ }
    public class ButtonState implements State { /*...*/ }
}
```

`State` 인터페이스를 구현하고 `Button`에 대한 특정 정보를 보유하는`ButtonState` 클래스를 정의한다. `getCurrentState` 메서드에서 이 클래스의 새 인스턴스를 생성한다. 

> `Java`에서는 다른 클래스에서 클래스를 선언하면 기본적으로 내부 클래스가 된다. 이 문제를 해결하려면 `ButtonState` 클래스를 정적으로 선언해야 한다. 

`Kotlin`에서 내부 클래스의 기본 동작은 다음과 같이 방금 설명한 것과 정반대이다.

```kotlin
class Button : View {
    override fun getCurrentState(): State = ButtonState()
    override fun restoreState(state: State) { /*...*/ }
    class ButtonState : State { /*...*/ }
}
```

명시적 수정자가 없는 `Kotlin`의 중첩 클래스는 `Java`의 정적 중첩 클래스와 동일하다. 외부 클래스에 대한 참조를 포함하도록 내부 클래스로 전환하려면 내부 수정자를 사용한다. 

![](https://velog.velcdn.com/images/cksgodl/post/c4ed24a7-ae07-44ee-9e34-1fd81262c84a/image.png)

- 그림 4.1 중첩 클래스는 외부 클래스를 참조하지 않는 반면 내부 클래스는 참조한다.

`Kotlin`에서 외부 클래스의 인스턴스를 참조하는 구문도 `Java`와 다르다. `Inner` 클래스에서 외부 클래스에 액세스하려면 `this@outer`를 작성한다.

```kotlin
class Outer {
    inner class Inner {
        fun getOuterReference(): Outer = this@Outer
    }
}
```

### 4.1.5 Enum 클래스: 제한된 클래스 계층 구조 정의하기

`when` 표현식에서는 가능한 모든 경우를 처리하는 것이 편리하다. 하지만 다른 브랜치가 일치하지 않는 경우 어떻게 해야 하는지 지정하려면 else 브랜치를 프로비저닝해야 한다.

```kotlin
interface Expr
class Num(val value: Int) : Expr
class Sum(val left: Expr, val right: Expr) : Expr
fun eval(e: Expr): Int =
    when (e) {
        is Num -> e.value
        is Sum -> eval(e.right) + eval(e.left)
        else -> throw IllegalArgumentException("Unknown expression")
}
```

표현식으로 `when` 구문을 사용하기 때문에(즉, 반환 값을 사용하기 때문에) `Kotlin` 컴파일러는 `else` 옵션을 강제로 추가해야한다. 이 예제에서는 의미 있는 값을 반 환할 수 없으므로 예외를 던진다.

항상 `else` 브랜치를 추가해야 하는 것은 편리하지 않다. 또한 사용자(또는 동료나 사용하는 의존성의 작성자)가 새 서브클래스를 추가하는 경우 컴파일러에서 케이스가 누락되었다는 알림을 보내지 않기 때문에 문제가 될 수 있다. 새 서브 클래스를 처리할 브랜치를 추가하는 것을 잊어버리면 기본 브랜치를 선택하기 때문 에 미묘한 버그가 발생할 수 있다.

`Kotlin`에는 이 문제를 해결할 수 있는 솔루션인 `sealed` 클래스가 있다. `sealed` 수정자를 사용하여 수퍼클래스를 표시하면 서브클래스를 만들 수 있는 가능성이 제한된다. 봉인된 클래스의 모든 직접 하위 클래스는 컴파일 시점에 봉인된 클래스 자체와 동일한 패키지에 선언되어야 하며 모든 하위 클래스는 동일한 모듈 내에 위치해야 한다.

```kotlin
sealed class Expr
class Num(val value: Int) : Expr()
class Sum(val left: Expr, val right: Expr) : Expr()

fun eval(e: Expr): Int =
    when (e) {
        is Num -> e.value
	    is Sum -> eval(e.right) + eval(e.left)
	}
```

`sealed` 클래스의 모든 서브클래스를 `when` 표현식으로 처리하는 경우 `else` 분기를 제공할 필요가 없다. 컴파일러가 가능한 모든 분기를 처리했는지 확인할 수 있기 때문이다.
`sealed` 수정자는 클래스가 추상적이라는 것을 의미하므로 명시적인 추상 수정자가 필요하지 않으며 추상 멤버를 선언할 수 있다는 점에 유의하라. 

![](https://velog.velcdn.com/images/cksgodl/post/353e4bf8-ae96-47a0-94a6-67b4025eb90d/image.png)

봉인된 클래스와 함께 `when`을 사용하고 새 하위 클래스를 추가하면 값을 반환하는 `when` 표현식이 컴파일에 실패하여 변경해야 하는 코드를 가리키게 된다

```kotlin
sealed class Expr
class Num(val value: Int) : Expr()
class Sum(val left: Expr, val right: Expr) : Expr()
class Mul(val left: Expr, val right: Expr): Expr()
fun eval(e: Expr): Int =
    when (e) {
        is Num -> e.value
        is Sum -> eval(e.right) + eval(e.left)
        // ERROR: 'when’ expression must be exhaustive,
        // add necessary 'is Mul' branch or 'else' branch instead
}
```

클래스외에도 `sealed` 수정자를 사용하여 `sealed` 인터페이스를 정의할수도 있다. `sealed` 인터페이스는 동일한 규칙을 따른다.

```kotlin
sealed interface Toggleable {
    fun toggle()
}
class LightSwitch: Toggleable {
    override fun toggle() = println("Lights!")
}
class Camera: Toggleable {
    override fun toggle() = println("Camera!")
	...and classes implement them.
}
```

봉인된 인터페이스의 모든 구현을 `when` 문에서 처리하면 다른 브랜치를 지정할 필요가 없다.

## 4.2 중요하지 않은 생성자나 프로퍼티가 있는 클래스 선언하기

객체 지향 언어에서 클래스는 일반적으로 하나 이상의 생성자를 가질 수 있다. `Kotlin`은 동일하지만 중요하고 명시적인 차이점이 있다. 

기본 생성자와 보조 생성자(클래스 본문에서 선언됨)를 구분한다. 또한 이니셜라이저 블록에 추가 초기화 로직을 넣을 수 있다. 

### 4.2.1 클래스 초기화하기: 기본 생성자 및 이니셜라이저 블록

```kotlin
class User(val nickname: String)
```

괄호로 둘러싸인 이 코드 블록을 기본 생성자라고 한다. 생성자 매개변수를 지정하고 해당 매 개변수에 의해 초기화되는 프로퍼티를 정의하는 두 가지 용도로 사용된다. 

```kotlin
class User constructor(_nickname: String) {
    val nickname: String	
    init {
        nickname = _nickname
	}
}
```

이 예제에서는 `constructor`와 `init`이라는 두 개의 새로운 `Kotlin` 키워드를 볼 수 있다. `constructor` 키워드는 기본 또는 보조 생성자 선언을 시작하고, `init` 키워드는 초기화 블록을 의미한다. 

```kotlin
class User(_nickname: String) { 
    val nickname = _nickname
}
```

이것은 동일한 클래스를 선언하는 또 다른 방법이다.

앞의 두 예제에서는 클래스 본문에서 `val` 키워드를 사용하여 프로퍼티를 선언 했다. 프로퍼티가 해당 생성자 매개변수로 초기화되는 경우 매개변수 앞에 `val` 키워드를 추가하여 코드를 간소화할 수 있다. 이렇게 하면 클래스 본문의 프로퍼티 정의가 대체된다.

```kotlin
class User(
    val nickname: String,
    val isSubscribed: Boolean = true
)
```

클래스의 인스턴스를 생성하려면 new와 같은 추가 키워드 없이 생성자를 직접 호출하면 된다. 

```kotlin
fun main() {
    val alice = User("Alice")
    println(alice.isSubscribed)
    val bob = User("Bob", false)
    println(bob.isSubscribed)
    // false
    val carol = User("Carol", isSubscribed = false)
    println(carol.isSubscribed)
    // false
    val dave = User(nickname = "Dave", isSubscribed = true)
    println(dave.isSubscribed)
    // true
}
```

수퍼클래스의 생성자가 인수를 받는다면 클래스의 기본 생성자도 인수를 초기화해야 한다. 베이스 클래스 목록의 슈퍼클래스 참조 뒤에 슈퍼클래스 생성자 매개변수를 제공하면 된다.

```kotlin
open class User(val nickname: String) { /* ... */ }
class SocialUser(nickname: String) : User(nickname) { /* ... */ }
```

(클래스에 대한 생성자를 선언하지 않으면 아무 작업도 수행하지 않는 매개변수가 없는 기본 생성자가 생성됨)

```kotlin
open class Button
```

Button 클래스에서 상속하고 생성자를 제공하지 않는 경우 슈퍼클래스에 파라메터 가 없더라도 명시적으로 슈퍼클래스의 생성자를 호출해야 한다. 그렇기 때문에 수퍼클래스 이름 뒤에 빈 괄호를 넣어야 한다.

```kotlin
class RadioButton: Button()
```

인터페이스와의 차이점에 유의하라. 인터페이스에는 생성자가 없으므로 생성자 인수의 이름을 명시적으로 지정할 수 없다. 따라서 인터페이스를 구현하는 경우 슈퍼타입 목록에서 이름 뒤에 괄호를 넣지 않는다. 

```kotlin
class Secret private constructor(private val agentName: String) {}
```

생성자를 비공개로 만들고 싶다면 위처럼 하면 된다.

`Secret` 클래스에는 비공개 생성자만 있기 때문에 클래스 외부의 코드는 이를 인스턴스화할 수 없다. `Java`에서는 클래스 인스턴스화를 금지하는 비공개 생성자를 사용하여 클래스가 정적 유틸리티 멤버의 컨테이너이거나 싱글톤이라는 보다 일반적인 아이디어를 표현할 수 있다. 

`Kotlin`에는 이러한 목적을 위한 언어 기능이 내장되어 있다. 정적 유틸리티로 최상위 함수를 사용한다. 싱글톤을 표현하려면 객체 선언을 사용한다.

대부분의 실제 사용 사례에서 클래스의 생성자는 매개 변수를 포함하지 않거나 해당 프로퍼티에 매개 변수를 할당하는 등 간단하다. 그렇기 때문에 `Kotlin`에는 기본 생성자에 대한 간결한 구문이 있으며 대부분의 경우 잘 작동한다. 하지만 인생이 항상 그렇게 쉬운 것은 아니므로 `Kotlin`에서는 클래스에 필요한 만큼의 생성자를 정의할 수 있다.

### 4.2.2 보조 생성자: 다양한 방법으로 슈퍼클래스 초기화하기

일반적으로 여러 생성자가 있는 클래스는 `Java`보다 `Kotlin` 코드에서 훨씬 덜 일반적이다. 오버로드된 생성자가 필요한 대부분의 상황은 기본 매개변수 값과 명명된 인수 구문에 대한 `Kotlin`의 지원으로 해결된다.

- 팁) 여러 개의 보조 생성자를 선언하여 인수를 오버로드하고 기본값을 제공하지 마라. 대신 기본값을 직접 지정하라.

하지만 여러 생성자가 필요한 상황도 여전히 존재한다. 가장 일반적인 경우는 클래스를 여러 가지 방식으로 초기화하는 여러 생성자를 제공하는 프레임워크 클래스를 확장해야 할 때이다. 예를 들어 `Java`로 선언되고 두 개의 생성자(하나는 문자열을, 다른 하나는 URI를 매개변수로 받는)가 있는 `Downloader` 클래스가 있을 것이다.

```kotlin
open class MyDownloader : Downloader {
	constructor(url: String?) : super(url) { 
        // some code
	}
    
    constructor(uri: URI?) : super(url) {
        // some code
	}
}
```

![](https://velog.velcdn.com/images/cksgodl/post/f3186405-fbcd-4756-8e60-9c3f53b71542/image.png)


### 4.2.3 인터페이스에서 선언된 속성 구현하기

Kotlin에서 인터페이스는 추상 속성 선언을 포함할 수 있다. 

```kotlin
interface User {
    val nickname: String
}
```

인터페이스를 구현하는 클래스는 닉네임 값을 가져오는 방법을 제공해야 한다. 이 인터페이스는 값을 뒷받침 필드에 저장할지 아니면 게터를 통해 가져올지 지정하지 않는다. 따라서 인터페이스 자체에는 어떤 상태도 포함하지 않는다.

인터페이스를 구현하는 클래스는 필요한 경우 값을 저장하거나 액세스 시 간단히 계산할 수 있다.

```kotlin
class PrivateUser(override val nickname: String) : User

class SubscribingUser(val email: String) : User {
    override val nickname: String
        get() = email.substringBefore('@')
}

class SocialUser(val accountId: Int) : User {
    override val nickname = getNameFromSocialNetwork(accountId)
}

fun getNameFromSocialNetwork(accountId: Int) =
    "kodee$accountId"

fun main() {
    println(PrivateUser("kodee").nickname)
    // kodee
    println(SubscribingUser("test@kotlinlang.org").nickname)
    // test
    println(SocialUser(123).nickname)
    // kodee123
}
```

```kotlin
interface EmailUser {
    val email: String
    val nickname: String
		get() = email.substringBefore('@')
}
```

이 인터페이스에는 추상 속성인 이메일과 사용자 지정 게터가 있는 닉네임 속성이 포함되어 있다. 첫 번째 속성은 서브클래스에서 재정의해야 하지만, 두 번째 속성은 필요에 따라 상속(또는 재정의)할 수 있다.

> 함수보다 속성을 선호해야 하는 경우
>
> 클래스의 특성은 일반적으로 프로퍼티로 선언하고 동작은 메서드로 선언해야 한다. 함수 대신 읽기 전용 프로퍼티를 사용하기 위한 몇 가지 추가 스타일 규칙이 `Kotlin`에 있다. 코드에 다음과 같은 특성이 있는 경우 함수보다 프로퍼티를 선호하라.
- 예외를 던지지 않음.
- 계산 비용이 저렴하다(또는 첫 번째 실행 시 캐시됨).
- 객체 상태가 변경되지 않은 경우 여러 호출에서 동일한 결과를 반환한다.
> 그렇지 않은 경우 함수를 대신 사용하는 것이 좋다.
인터페이스에 구현된 프로퍼티와 달리 클래스에 구현된 프로퍼티는 백킹 필드에 대한 전체 액세스 권한을 가진다. 

### 4.2.4 게터 또는 세터에서 백킹 필드에 액세스하기

값을 저장하고 값에 액세스하거나 수정할 때 실행되는 추가 로직을 제공하는 프로퍼티를 구현하는 방법을 살펴보자. 이를 지원하려면 프로퍼티의 백킹 필드에 액세스할 수 있어야 한다. 

```kotlin

class User(val name: String) {
    var address: String = "unspecified"
		set(value: String) {
    		println(
	        	"""
		        Address was changed for $name:
    		    "$field" -> "$value".
        		""".trimIndent()
			)
    		field = value
		}
}

fun main() {
    val user = User("Alice")
    user.address = "Christoph-Rapparini-Bogen 23"
    // Address was changed for Alice:
    // "unspecified" -> "Christoph-Rapparini-Bogen 23".
}
```

평소처럼 `user.address = "새 값"`으로 프로퍼티 값을 변경하면 내부적으로 해당 세터가 호출된다. 이 예제에서는 세터가 재정의되었으므로 추가 로깅 코드가 실행된다.

세터 본문에서 특수 식별자 필드를 사용하여 뒷받침 필드의 값에 액세스한다. 게터에서는 값을 읽을 수만 있고, 세터에서는 값을 읽고 수정할 수 있다.

가변 속성에 대한 게터 또는 세터가 사소한 경우 다른 접근자를 재정의하지 않고 사용자 정의 동작이 필요한 곳에만 접근자를 정의하도록 선택할 수 있다는 점에 유의하라.

백킹 필드가 있는 프로퍼티와 없는 프로퍼티의 차이점이 무엇인지 궁금할 수 있다. 프로퍼티에 액세스하는 방식은 프로퍼티에 뒷면 필드가 있는지 여부에 따라 달라지지 않으며, 명시적으로 참조하거나 기본 접근자 구현을 사용하는 경우 컴파일러가 프로퍼티에 대한 백킹 필드를 생성한다. 필드를 사용하지 않는 사용자 정의 접근자 구현을 제공하는 경우 컴파일러는 프로퍼티가 정보 자체를 저장할 필요가 없다고 간주하므로 백킹 필드가 생성되지 않는다. 

```kotlin
class Person(var birthYear: Int) {
    var ageIn2050
		get() = 2050 - birthYear // 게터에 필드 참조가 없다.
		set(value) {
    		birthYear = 2050 - value // 세터는백킹필드가 생성되지 않음을 의미
		}
}
```

### 4.2.5 액세서리 가시성 변경

기본적으로 접근자의 `public` 여부는 프로퍼티의 공개 여부와 동일하다. 그러나 필요한 경우 `get` 또는 `set` 키 단어앞에 가시성 수정자를 넣어 이를 변경할 수 있다. 

```kotlin
class LengthCounter {
    var counter: Int = 0
		private set

	fun addWord(word: String) {
        counter += word.length
	}
}
```

카운터 프로퍼티는 클래스가 클라이언트에 제공하는 API의 일부이므로 `public`이다. 하지만 외부 코드가 변경하여 잘못된 값을 저장할 수 있으므로 클래스 내에서만 수정되도록 해야 한다.
따라서 컴파일러가 기본 가시성을 가진 게터를 생성 하도록하고 설정자의 가시성을 비공개로 변경했다.

```kotlin
fun main() {
    val lengthCounter = LengthCounter()
    lengthCounter.addWord("Hi!")
    println(lengthCounter.counter)
    // 3
}

fun main() {
    // ...
	lengthCounter.counter = 0
	// Error: Cannot assign to 'counter': the setter is private in  ̄ 'LengthCounter'
}
```

## 4.3 컴파일러 생성 메서드: 데이터 클래스 및 클래스 위임

`Java` 플랫폼은 많은 클래스에 존재해야 하며 일반적으로 기계적 방식으로 구현되는 몇 가지 메서드를 정의하는데, 예를 들어 `equals`(두 객체가 서로 같은지 여부를 나타내는), `hashCode`(해시 맵 같은 데이터 구조에 필요한 객체의 해시 코드 제공), `toString`( 객체의 텍스트 재현을 반환하는) 등이 있다.

다행히도 `IDE`는 이러한 메서드 생성을 자동화할 수 있으므로 일반적으로 직접 작성할 필요가 없다. 하지만 이 경우에도 코드베이스에는 여전히 유지 관리해야 하는 보일러 플레이트 코드가 포함되어 있다. `Kotlin` 컴파일러는 한 단계 더 나아가 소스 코드 파일을 복잡하게 만들지 않고 기계적인 코드 생성을 백그라운드에서 수행할 수 있다.

### 4.3.1 범용 객체 메서드

모든 `Kotlin` 클래스에는 `Java`에서와 마찬가지로 재정의할 수 있는 몇 가지 메서드, 즉 `toString`, `equals` 및 `hashCode`가 있다. 이러한 메서드가 무엇인지, 그리고 `Kotlin`이 어떻게 자동으로 구현을 생성하는 데 도움을 줄 수 있는지 살펴보겠다. 

```
class Customer(val name: String, val postalCode: Int)
```

`Java`에서와 마찬가지로 `Kotlin`의 모든 클래스는 클래스 객체의 문자열 표현을 가져오는
방법을 제공한다. 이 기능은 주로 디버깅 및 로깅에 사용되지만 다른 컨텍스트에서도 이 기능을 사용할 수 있다. 기본적으로 객체의 문자열 표현은 Customer@5eef23b4(클래스 이름과 객체가 저장된 메모리 주소)처럼 보이지만 실제로는 그다지 유용하지 않다.

따라서 이를 효율적으로 활용하기 위해 이를 재정의 한다.

```kotlin
 class Customer(val name: String, val postalCode: Int) {
	override fun toString() = "Customer(name=$name, postalCode=$postalCode)"
}
```

#### 객체 동일성: equals()

`Customer` 클래스의 모든 연산은 이 클래스 외부에서 이루어진다. 이 클래스는 데이터를 저장할 뿐이므로 단순하고 투명해야 한다. 그럼에도 불구하고 이러한 클래스의 동작에 대한 몇 가지 요구 사항이 있을 수 있다. 예를 들어 객체에 동일한 데이터가 포함되어 있는 경우 객체를 동일하게 간주하고 싶다고 가정해보겠다.

```kotlin
fun main() {
    val customer1 = Customer("Alice", 342562)
    val customer2 = Customer("Alice", 342562)
    println(customer1 == customer2)
    // false
}
// In Kotlin에서==는 참조가 아닌 객체가 동일한지 여부를 확인한다. equals로 컴파일된다.
```

> == 과 equals 에 대해
>
> `Java`에서는 == 연산자를 사용하여 원시 타입과 참조 타입을 비교할 수 있다. 원시 타입에 적용하면 `Java`의 ==는 값을 비교하는 반면, 참조 타입에서 ==는 참조를 비교한다.
>
> `Kotlin`에서 == 연산자는 두 개체를 비교하는 기본 방법으로, 내부적으로 euqals 함수를 호출하여 값을 비교한다. 따라서 클래스에서 ==가 재정의된 경우 ==를 사용하여 해당 인스턴스를 안전하게 비교할 수 있다. 참조 비교의 경우 객체 참조를 비교하여 `Java`의 ==와 정확히 동일하게 작동하는 === 연산자를 사용할 수 있다. 즉, `===`는 두 참조가 메모리에서 동일한 객체를 가리키는지 여부를 확인한다. 그리고 ==와 ===의 부정적 아날로그인 !=와 !==는 그에 따라 동일한 로직으로 작동한다.

```kotlin
class Customer(val name: String, val postalCode:
    override fun equals(other: Any?): Boolean {
		if (other == null || other !is Customer)
    		return false
		}
        return name == other.name && postalCode == other.postalCode

	override fun toString() = "Customer(name=$name, postalCode=$postalCode)"
}
```

위의 코드는 ==연산의 경우 정상 작동한다. 하지만 더 복잡한 작업을 수행하려는 경우에는 작동하지 않는다. 이유는 해시코드가 누락된 것이 문제라고 말할 수 있다. 해시코드가 무엇이고 이것이 왜 중요한지 알아보겠다.

#### 해시 컨테이너: 해시코드()

해시코드 메서드는 항상 같음과 함께 재정의 해야한다. 이 섹션에서는 그 이유를 설명한다.

```kotlin
fun main() {
    val processed = hashSetof(Customer("Alice", 342562))
    println(processed.contains(Customer("Alice", 342562)))
    // false
}
```

위의 예제는 왜 false를 반환할까? 

이는 `Customer` 클래스에 `hashCode` 메서드가 없기 때문이다. 따라서 두 객체가 동일한 경우 동일한 해시코드를 가져야 한다는 일반적인 해시코드 컨트랙트를 위반한다. 

__처리된 집합은 해시셋이다. 해시셋의 값은 최적화된 방식으로 비교된다. 처음에는 해시코드가 비교되고, 해시코드가 동일한 경우에만 실제값이 비교된다.__

위의 예제에서 `Customer` 클래스의 서로 다른 두 인스턴스의 해시코드가 다르므로 equals가 참을 반환하더라도 집합은 두 번째 객체를 포함하지 않는 것으로 판단한다. 따라서 규칙을 따르지 않으면 해시집합과 같은 데이터구조가 올바르게 작동할 수 없다.
아래처럼 적절한 해시코드 구현을 제공해야 한다.

```kotlin
class Customer(val name: String, val postalCode: Int) {
    /* ... */
    override fun hashCode(): Int = name.hashCode() * 31 + postalCode
}
```

## 4.3.2 데이터 클래스: 범용 메서드를 자동 생성 함

클래스가 데이터의 편리한 홀더가 되려면 `toString, equals` 및 `hashCode`와 같은 메서드를 재정의해야 한다. 

좋은 소식은 이러한 메서드를 모두 `Kotlin`에서 생성할 필요는 없다는 것이다. `data` 수정자를 추가하면 필요한 메서드가 자동으로 생성된다.

```kotlin
data class Customer(val name: String, val postalCode: Int)
```

쉽죠? 이제 일반적으로 필요한 모든 표준 메서드를 재정의하는 클래스가 생겼다. 아래 마법같은 예제를 살펴보자.

```kotlin
fun main() {
    val c1 = Customer("Sam", 11521)
    val c2 = Customer("Mart", 15500)
    val c3 = Customer("Sam", 11521)
    println(c1)
    // Customer(name=Sam, postalCode=11521)
    println(c1 == c2)
    // false
    println(c1 == c3)
    // true
    println(c1.hashCode())
    // 2580770
    println(c3.hashCode())
    // 2580770
}
```

#### 데이터 클래스와 불변성: 복사 메서드

데이터 클래스의 프로퍼티가 반드시 `val`일 필요는 없고, `var`도 사용할 수 있지만, 데이터 클래스의 인스턴스를 변경 불가능하게 만드는 읽기 전용 프로퍼티만 사용할 것을 강력히 권장한다. 

그렇지 않으면 키로 사용되는 객체가 컨테이너에 추가된 후 수정되면 컨테이너가 유효하지 않은 상태가 될 수 있으므로 이러한 인스턴스를 해시맵이나 유사한 컨테이너의 키로 사용하려는 경우 이 작업이 필요하다. 불변 객체는 특히 멀티스레드 코드에서 추론하기가 훨씬 쉽다. 객체가 생성되면 원래 상태로 유지되므로 코드가 작업하는 동안 다른 스레드가 객체를 수정하는 것에 대해 걱정할 필요가 없다.

데이터 클래스를 불변 객체로 더욱 쉽게 사용할 수 있도록 `Kotlin` 컴파일러는 클래스의 인스턴스를 복사하여 일부 속성 값을 변경할 수 있는 메서드를 하나 더 생성한다. 복사본을 만드는 것은 일반적으로 인스턴스를 제자리에서 수정하는 것보다 선호되는 대안이다. 복사본은 별도의 수명 주기를 가지며 코드에서 원본 인스턴스를 참조하는 위치에 영향을 줄 수 없기 때문이다. 

복사 메서드를 수동으로 구현할 경우 의 모습은 다음과 같다:

```kotlin
class Customer(val name: String, val postalCode: Int) {
    /* ... */
    fun copy(name: String = this.name,
             postalCode: Int = this.postalCode) =
        Customer(name, postalCode)
}

fun main() {
    val bob = Customer("Bob", 973293)
    println(bob.copy(postalCode = 382555))
    // Customer(name=Bob, postalCode=382555)
}
```

### 4.3.3 수업 위임: by 키워드 사용

대규모 객체 지향 시스템을 설계할 때 흔히 발생하는 문제는 구현 상속으로 인한 취약성이다. 클래스를 확장하고 그 메서드 중 일부를 재정의하면 코드가 확장 중인 클래스의 구현 세부 사항에 종속된다. 시스템이 발전하여 기본 클래스의 구현이 변경되거나 새로운 메서드가 추가되면 클래스에서 설정한 동작에 대한 가정이 유효하지 않게 되어 코드가 제대로 동작하지 않을 수 있다.

이전 절에서 살펴본 것처럼 `Kotlin`의 설계는 이 문제를 인식하고 기본적으로 클래스를 최종 클래스로 취급한다. 이렇게 하면 확장성을 위해 설계된 클래스만 상속 할 수 있다. 이러한 클래스에서 작업할 때 클래스가 열려 있음을 알 수 있으며, 수정 사항이 파생된 클래스와 호환되어야 한다는 점을 염두에 둘 수 있다.

그러나 종종 확장하도록 설계되지 않았더라도 다른 클래스에 동작을 추가해야 하는 경우가 있다. 이를 구현하는 일반적인 방법을 데코레이터 디자인 패턴이라한다. 

아래는 데코레이터 디자인 패턴의 예제이다.

```kotlin
class DelegatingCollection<T> : Collection<T> {
    private val innerList = arrayListOf<T>()
    override val size: Int get() = innerList.size
    override fun isEmpty(): Boolean = innerList.isEmpty()
    override fun contains(element: T): Boolean = innerList.contains(element)
    override fun iterator(): Iterator<T> = innerList.iterator()
    override fun containsAll(elements: Collection<T>): Boolean =
            innerList.containsAll(elements)
}
```

__이 패턴의 핵심은 원래 클래스와 동일한 인터페이스를 구현하고 원래 클래스의 인스턴스를 필드로 저장하는 새 클래스가 생성된다는 것이다.__

원래 클래스의 동작을 수정할 필요가 없는 메서드는 원래 클래스 인스턴스로 전달된다. 이 접근 방식의 한 가지 단점은 상당히 많은 양의 보일러 플레이트 코드가 필요하다는 점이다.

좋은 소식은 `Kotlin`이 언어 기능으로 위임에 대한 최고 수준의 지원을 제공한다는 점이다. 인터페이스를 구현할 때 마다 `by` 키워드를 사용하여 인터페이스 구현을 다른 객체에 위임한다고 말할 수 있다. 이 접근 방식을 사용하여 이전 예제를 다시 작성하는 방법은 다음과 같다:

```kotlin
class DelegatingCollection<T>(
    innerList: Collection<T> = mutableListOf<T>()
) : Collection<T> by innerList
```

클래스의 모든 메서드 구현이 사라졌다. 컴파일러가 이를 생성하며, 구현은 `DelegatingCollection` 예제의 구현과 유사하다. 코드에 흥미로운 내용이 거의 없기 때문에 컴파일러가 자동으로 동일한 작업을 수행할 수 있는데 굳이 수동으로 작성할 필요가 없다.

이제 일부 메소드의 동작을 변경해야 하는 경우 해당 메소드를 재정의하면 생성 된 메소드 대신 사용자 코드가 호출된다. 기본 인스턴스에 위임하는 기본 구현에 만족하는 메서드는 제외할 수 있다.

```kotlin
class CountingSet<T>(
    private val innerSet: MutableCollection<T> = hashSetOf<T>()
) : MutableCollection<T> by innerSet {
    var objectsAdded = 0
    override fun add(element: T): Boolean {
        objectsAdded++
        return innerSet.add(element)
	}
    override fun addAll(elements: Collection<T>): Boolean {
        objectsAdded += elements.size
	} 
}

fun main() {
    val cset = CountingSet<Int>()
    cset.addAll(listOf(1, 1, 2))
    println("Added ${cset.objectsAdded} objects, ${cset.size} uniques.")
    // Added 3 objects, 2 uniques.
}
```

보시다시피, `add`와 `addAll` 메서드를 재정의하여 개수를 늘리고, 나머지 `MutableCollection` 인터페이스 구현은 래핑하는 컨테이너에 위임한다.

중요한 부분은 기본 컬렉션이 구현되는 방식에 대한 종속성을 도입하지 않는다는 것이다. 예를들어, 해당 컬렉션이 `addAll`을 루프에서 호출하여 구현하든, 특정경우에 최적화된 다른 구현을 사용하든 상관하지 않는다. 클라이언트 코드가 클래스를 호출 할 때 어떤 일이 발생하는지 완전히 제어할 수 있으며, 기반 컬렉션의 문서화된 API에 만 의존하여 연산을 구현하므로 계속 작동하는 컬렉션을 신뢰할 수 있다. 

## 4.4 object 키워드: 클래스 선언과 인스턴스 생성, 결합하기

`object` 키워드는 `Kotlin`에서 여러 가지 경우에 등장하지만 모두 동일한 핵심 아이디어를 공유한다. 이 키워드는 클래스를 정의하고 동시에 해당 클래스의 인스턴스(즉, 객체)를 생성한다는 점이다. 이 키워드가 사용되는 다양한 상황을 살펴보겠다:

- 객체 선언 - 싱글톤을 정의하는 방법.
- 컴패니언객체 - 이 클래스와 관련이 있지만 클래스 인스턴스를 호출할 필요가없는 팩토리 메서드 및 기타 메서드를 포함한다. 클래스 이름을 통해 해당
멤버에 액세스할 수 있다.
- 객체표현식 - `Java`의 익명 내부 클래스 대신 사용된다.

### 4.4.1 object 선언: 간편한 싱글톤

객체 지향 시스템을 설계할 때 흔히 발생하는 경우가 인스턴스가 하나만 필요한 클래스이다. 이는 일반적으로 `Java`와 같은 언어에서 싱글톤 패턴을 사용하여 구현되는데, 개인 생성자와 클래스의 유일한 기존 인스턴스를 보유하는 정적 필드가 있는 클래스를 정의한다.

`Kotlin`은 객체 선언 기능을 사용하여 이를 위한 최고 수준의 언어 지원을 제공한다. 객체 선언은 클래스 선언과 해당 클래스의 단일 인스턴스 선언을 결합한다.

```kotlin
object Payroll {
    val allEmployees = mutableListOf<Person>()
    fun calculateSalary() {
        for (person in allEmployees) {
			/* ... */ 
    	}
	}
}
```

`object` 선언은 하나의 문에서 같은 이름을 가진 클래스와 해당 클래스의 변수를 효과적으로 정의한다.

클래스와 마찬가지로 객체 선언에는 프로퍼티, 메서드, 이니셜라이저 블록 등의 선언이 포함될 수 있다. 허용되지 않는 유일한 것은 생성자(기본 또는 보조)이다. 일반 클래스의 인스턴스와 달리 객체 선언은 코드의 다른 위치에서 생성자 호출을 통하지 않고 정의 시점에 즉시 생성된다. 

변수와 마찬가지로 `object`를 사용하면. 문자 왼쪽에 있는 객체 이름을 사용 하여 메서드를 호출하고 프로퍼티에 액세스할 수 있다:

```kotlin
Payroll.allEmployees.add(Person(/* ... */))
Payroll.calculateSalary()
```

`object`는 클래스 및 인터페이스에서 상속할 수도 있다. 이는 사용 중인 프레임워크에서 인터페이스를 구현해야 하지만 구현에 상태가 포함되어 있지 않을 때 유용하다.

```kotlin

object CaseInsensitiveFileComparator : Comparator<File> {
    override fun compare(file1: File, file2: File): Int {
        return file1.path.compareTo(file2.path,
                ignoreCase = true)
	} 
}
fun main() {
    println(CaseInsensitiveFileComparator.compare(File("/User"), File("/user")))
	// 0
}
```

일반 객체(클래스의 인스턴스)를 사용할 수 있는 모든 컨텍스트에서 싱글톤 객체를 사용할 수 있다.

```kotlin
fun main() {
    val files = listOf(File("/Z"), File("/a"))
    println(files.sortedWith(CaseInsensitiveFileComparator))
    // [/a, /Z]
}
```

> __싱글톤 및 종속성주입 (DI)__
싱글톤 패턴과 마찬가지로 객체 선언이 대규모 소프트웨어 시스템에서 사용하기에 항상 이상적인 것은 아니다. 깊이가 거의 또는 전혀 없는 작은 코드 조각에는 적합하지만 시스템의 다른 많은 부분과 상호 작용하는 대규모 컴포넌트에는 적합하지 않다. 주된 이유는 객체의 인스턴스화를 제어할 수 없고 생성자에 대한 매개변수를 지정할 수 없기 때문이다.
>
> 즉, 단위 테스트 또는 소프트웨어 시스템의 다른 구성에서 객체 자체의 구현이나 객체가 종 속된 다른 클래스를 대체할 수 없다. 그렇게 해야 하는 경우 일반 `Kotlin` 클래스와 종속성 주입을 사용해야 한다.


클래스 안에 `object`를 선언할 수도 있다. 그렇다고, 클래스의 각 인스턴스에 대해 별도의 인스턴스를 갖지 않는다. 

```kotlin
data class Person(val name: String) {
    object NameComparator : Comparator<Person> {
        override fun compare(p1: Person, p2: Person): Int =
            p1.name.compareTo(p2.name)
	} 
}

fun main() {
	val persons = listof(Person("Bob"), Person("Alice")) 
    println(persons.sortedWith(Person.NameComparator))
    // [Person(name=Alice), Person(name=Bob)]
}
```

> __Java에서 Kotlin 개체 사용__
`Kotlin`의 객체 선언은 항상 `INSTANCE`라는 이름의 정적 필드가 있는 클래스로 컴파일되며, 이 클래스는 항상 싱글톤 인스턴스를 보유한다. `Java`에서 싱글톤 패턴을 구현했다면 아마 수작업으로 동일한 작업을 수행했을 것이다. 따라서 `Java` 코드에서 `Kotlin` 객체를 사용하려면 정적 INSTANCE 필드에 액세스한다:
>
> `INSTANCE.compare(file1, file2); Person.NameComparator.INSTANCE.compare(person1, person2)`

### 4.4.2 컴패니언 객체: 팩토리 메서드와 정적 멤버를 위한 공간

`Kotlin`의 클래스는 `static` 멤버를 가질 수 없다. 실제로 `Kotlin`에는 `Java`처럼 `static` 키 단어가 없다. 대신 `Kotlin`은 패키지 수준 함수와 `object`에 의존한다. 

대부분의 경우 최상위 수준 함수를 사용하는 것이 좋다. 그러나 최상위 함수는 클래스의 비공개 메모리에 액세스할 수 없다. 프라이빗 멤버에 액세스해야 하는함수의 예로 팩토리 메서드를 들 수 있다. 팩토리 메서드는 객체 생성을 담당하므로 비공개 멤버에 대한 액세스가 필요하다.

![](https://velog.velcdn.com/images/cksgodl/post/94407434-a6dd-45e2-b21a-025af3f4bb7a/image.png)

클래스에 정의된 객체 선언 중 정확히 한 개를 특수 키워드인 `companion`으로 표시할 수 있다. 이렇게 하면 객체 이름을 명시적으로 지정하지 않고도 포함된 클래스 이름을 통해 해당 객체의 메서드와 프로퍼티에 직접 액세스할 수 있다.

```kotlin
class MyClass {
    companion object {
        fun callMe() {
            println("Companion object called")
}	 }
}
fun main() {
    MyClass.callMe()
    // Companion object called
}
```

컴패니언 객체는 해당 클래스에 속한다는 점을 명심해야 한다. 클래스의 인스턴스에서는 컴패니언 객체의 멤버에 액세스할 수 없다.

```kotlin

fun main() {
	val myobject = MyClass() myobject.callMe()
	// 오류: 해결되지 않은 참조: callMe 
}
```

컴패니언 객체는 비공개 생성자를 포함해 클래스의 모든 비공개 멤버에 액세스할 수 있다. 따라서 팩토리 패턴을 구현하기에 이상적인 후보이다.

생성자 두 개를 선언한 다음 컴패니언 객체에 선언된 팩토리 메서드를 사용하도록 변경하는 예제를 살펴보겠다.

```kotlin
class User {
    val nickname: String
    constructor(email: String) {
        nickname = email.substringBefore('@')
	} 
    constructor(socialAccountId: Int) {
        nickname = getSocialNetworkName(socialAccountId)
	}
}
```

```kotlin
class User private constructor(val nickname: String) {
	companion object {
    	fun newSubscribingUser(email: String) =
			User(email.substringBefore('@'))

		fun newSocialUser(accountId: Int) =
    		User(getNameFromSocialNetwork(accountId)
	}
}
```

```kotlin
fun main() {
	val subscribingUser = User.newSubscribingUser("bob@gmail.com") 
    val socialUser = User.newSocialUser(4) 
    println(subscribingUser.nickname)
	// 밥 
}
```

팩토리 메서드는 매우 유용하다. 예시와 같이 목적에 따라 이름을 지정할 수 있다. 또한 `SubscribingUser`와 `SocialUser`가 클래스인 예제에서와 같이 팩토리 메서드는 메서드가 선언된 클래스의 서브클래스를 반환할 수 있다. 또한 필요하지 않은 경우 새 객체를 만들지 않을 수도 있다.

### 4.4.3 일반 객체로서의 컴패니언 객체

컴패니언 객체는 클래스에서 선언된 일반 객체이다. 다른 객체 선언과 마찬가지로 이름을 지정하거나 인터페이스를 구현하거나 확장 함수나 프로퍼티를 가질 수 있다.

```kotlin
class Person(val name: String) {
    companion object Loader {
		fun fromJSON(jsonText: String): Person = /* ... */
	} 
}
```

대부분의 경우 컴패니언 객체를 포함하는 클래스의 이름을 통해 참조하므로 이름에 대해 걱정할 필요가 없다. 하지만 필요한 경우 `Loader`와 같이 이름을 지정할 수 있다.

클래스는 하나의 동반자 개체만 가질 수 있다. 

`Kotlin` 표준 라이브러리에서도 이러한 싱글톤 컴패니언 객체를 다수 찾을 수 있다. 예를들어, 컴패니언 오브젝트인 `Kotlin`의 `Random` 이 있다.

```kotlin
val chance = Random.nextInt(from = 0, until = 100)
val coin = Random.Default.nextBoolean()
```

컴패니언 객체도 인터페이스를 구현할 수 있다.

```kotlin
interface JSONFactory<T> {
    fun fromJSON(jsonText: String): T
}

class Person(val name: String) {
	
    companion object : JSONFactory<Person> {
    	override fun fromJSON(jsonText: String): Person = /* ... */
	}
}
```

#### 컴패니언 개체 확장

확장 함수를 사용하면 코드베이스의 다른 곳에 정의된 클래스 의 인스턴스에서 호출할 수 있는 메서드를 정의할 수 있다. 하지만 컴패니언 객체 메서드와 동일한 구문을 사용하여 클래스 자체에서 호출할 수 있는 함수를 정의해야 하는 경우에는 어떻게 해야 할까? 클래스에 컴패니언 객체가 있는 경우 해당 객체에 확장 함수를 정의하면 된다. 

좀 더 구체적으로 설명하자면, C 클래스에 컴패니언 객체가 있고 `C.Companion`에 확장함수 `func`를 정의한 경우 이를 `C.func()`로 호출할 수 있다. 

예를들어 `Person`클래스에 대한 관심사를 더 깔끔하게 분리하고 싶다고 가정해보겠다. 

```kotlin
class Person(val firstName: String, val lastName: String) {
	companion object {
	}	 
}

fun Person.Companion.fromJSON(json: String): Person {
}
```

`Json`에서 컴패니언 객체의 메서드로 정의된 것처럼 호출하지만 실제로는 외부에 확장 함수로 정의되어 있다. 항상 그렇듯이 이 확장 함수는 멤버처럼 보이지만 멤버가 아니다.

### 4.4.4 객체표현식: 익명 내부 클래스 표현 변경

`object` 키워드는 명명된 싱글톤과 같은 객체를 선언할 때뿐만 아니라 익명 객체를 선언할 때도 사용할 수 있다. 익명 객체는 Java의 익명 내부 클래스 사용을 대체한다.

예를 들어 `Kotlin`에서 일반적인 이벤트 리스너를 제공하는 방법을 살펴보다. 

```kotlin
interface MouseListener {
    fun onEnter()
    fun onClick()
}
class Button(private val listener: MouseListener) { /* ... */ }
```

객체 표현식을 사용하여 마우스-리스너 인터페이스의 임시구현을 만든 다음 `Button` 생성자에 전달할 수 있다.

```kotlin
fun main() {
    Button(object : MouseListener {
        override fun onEnter() { /*... */ }
        override fun onClick() { /*... */ }
	})
}
```

`Kotlin`의 익명 개체는 매우 유연하여 하나의 인터페이스, 여러 인터페이스 또는 인터 페이스를 전혀 구현하지 않을 수 있다.

객체 표현식의 코드는 `Java`의 익명 클래스에서와 마찬가지로 해당 코드가 생성 된 함수의 변수에 액세스할 수 있다. 하지만 `Java`와 달리 최종 변수로만 제한되지 않는다. `Kotlin`에서는 객체 표현식 내에서 변수 값을 수정할 수도 있다. 

```kotlin
fun main() {
	var clickCount = 0  
	Button(object : MouseListener {
        override fun onEnter() { /* ... */ }
        override fun onClick() {
			clickCount++ 
		}})
}
```

`object` 표현식은 익명 객체에서 여러 메서드를 재정의해야 할 때 주로 유용하다. 단일 메서드 인터페이스(예: `Runnable`)만 구현해야 하는 경우 `Kotlin`의 `SAM` 변환 지원을 활용하여 구현을 함수 리터럴(람다)로 작성할 수 있다.

## 4.5 오버헤드 없는 추가 유형: 인라인 클래스

데이터 클래스를 통해 컴파일러에서 생성된 코드가 코드를 가독성 있고 깔끔하게 유지하는 데 어떻게 도움이 되는지 이미 살펴보았다. `Kotlin` 컴파일러의 강력한 기능을 보여주는 또 다른 예제인 인라인 클래스를 살펴보겠다.

아래 예제를 살펴보자.

```kotlin
fun addExpense(expense: Int) {
    // save the expense as USD cent
}
```

일본 여행에서 200엔짜리 맛있는 니쿠만 구매하고 싶다.

```kotlin
addExpense(200) // 일본 엔화
```

함수의 서명이 일반 Int를 허용하기 때문에 함수 호출자가 실제로는 다른 의미를 가진 값을 전달하는 것을 막을 수 있는 방법이 없다는 점이 문제이다. 이 경우 실 제 구현에서는 전달된 값이 "USD 센트"를 의미해야 하지만 호출자가 매개변수를 "엔"으로 해석하는 것을 막을 수 있는 방법은 없다.

이를 방지하는 고전적인 접근 방식은 일반 Int 대신 클래스를 사용하는 것이다:

```kotlin
class UsdCent(val amount: Int) 
fun addExpense(expense: UsdCent) {
	// 비용을 USD 센트로 저장 
}

fun main() { 
	addExpense(UsdCent(147))
}
```


이 접근 방식을 사용하면 실수로 잘못된 의미의 값을 함수에 전달할 가능성이 훨씬 줄어 들지만 몇 가지 성능 고려 사항이 있다. 각 `addExpense` 함수 호출마다 새 `UsdCent` 객체를 생성해야 하며, 이 객체는 함수 본문에서 언래핑되어 버려져야 한다는 점이다. 이 함수가 많이 호출되는 경우 수명이 짧은 객체를 대량으로 할당하고 가비지 컬렉션을 수행해야 한다.

인라인 클래스가 바로 여기에 적합하다. 인라인 클래스를 사용하면 성능 저하 없이 사용할 수 있다.

`UsdCent`클래스를 인라인 클래스로 전환하려면 값 키워드로 표시한 다음`@JvmInline`으로 주석을 달면 된다:

```kotlin
@JvmInline
value class UsdCent(val amount: Int)
```

이 작은 변경으로 `UsdCent` 래퍼 유형이 제공하는 유형 안전성을 포기하지 않고도 객체의 불필요한 인스턴스화를 방지할 수 있다. 런타임에 `UsdCent`의 인스턴스는 래핑된 프로퍼티로 표시된다. 인라인 클래스의 이름도 여기에서 유래한 것으로, 클래스의 데이터는 사용 사이트에서 인라인 처리된다.

참고 정확하게 표현하기 위해 `Kotlin` 컴파일러는 가능한 경우 인라인 클래스를 원시타입으로 표시한다. 참조 유형을 유지해야 하는 경우가 있는데, 특히 인라인 클래스가 매개 변수로 사용되는 경우가 대표적이다. 이러한 특수한 경우에 대한 논의는 Kotlin 설명서(https://kotlinlang.org/docs/inline-classes.html)에서 확인할 수 있다.

"인라인" 자격을 갖추려면 클래스에 정확히 하나의 프로퍼티가 있어야 하며, 이 프로퍼티는 기본 생성자에서 인라인화되어야 한다. 인라인 클래스는 또한 클래스 계층 구조에 참여하지 않는다. 다른 클래스를 확장하지 않으며 스스로 확장할 수도 없다. 

그러나 인터페이스를 구현하거나 메서드를 정의하거나 계산된 프로퍼티를 제공할 수는 있다:

```kotlin
interface PrettyPrintable {
    fun prettyPrint()
}
@JvmInline
value class UsdCent(val amount: Int): PrettyPrintable {
    val salesTax get() = amount * 0.06
    override fun prettyPrint() = println("${amount}¢")
}
fun main() {
    val expense = UsdCent(1_99)
    println(expense.salesTax)
    // 11.94
    expense.prettyPrint()
    // 199¢
}
```

일반 숫자 유형에 사용되는 측정 단위를 표시하거나 다른 문자열의 의미를 구분하는 등 기본 값의 의미를 명확히 하기 위해 인라인 클래스를 주로 사용한다.

현재 인라인 클래스는 `Kotlin` 컴파일러의 기능이다. 대부분의 경우 객체 할당으로 인한 성능 저하가 발생하지 않는 코드를 방출하는 방법을 알고 있다. 하지만 언제까지나 그럴 필요는 없다. 프로젝트 발할라(https://openjdk.org/projects/valhalla/)는 인라인 클래스에 대한 지원을 `JVM` 자체로 가져오는 것을 목표로 하는 일련의 JDK 개선 제안(JEP)이다. (이는 런타임 환경이 기본적 으로 인라인 클래스의 개념을 이해하지 못한다는 것을 의미한다.)

따라서 현재 `Kotlin`의 인라인 클래스가 `@JvmInline`으로 어노테이션되는 이유도 `Valhalla` 때문이다. 이를 통해 현재 인라인 클래스가 `Kotlin` 컴파일러에서 특별한 대우를 받고 있음을 명시적으로 알 수 있다. 향후 `Valhalla` 기반 구현이 제공되면 어노테이션 없이도 `Kotlin`에서 인라인 클래스를 선언하고 기본적으로 내장된 JVM 지원을 활용할 수 있다.

## 요약

- `Kotlin`의 인터페이스는 `Java`와 유사하지만 기본 구현 및 속성을 포함할 수 있다.
- 모든 클래스는 기본적으로 `final`, `public`이다.
- 선언을 최종 선언이 아닌 것으로 만들려면 `open`을 사용한다.
- 내부 선언은 동일한 모듈에서 볼 수 있다.
- 중첩 클래스는 기본적으로 내부 클래스가 아니다. 외부 클래스에 대한 참조
를 저장하려면 `inner` 키워드를 사용하라.
- `sealed` 클래스의 모든 직접 서브클래스와 `sealed` 인터페이스의 모든 구현은 컴파일시점에 알 수 있어야 한다.
- 이니셜라이저 블록과 보조 생성자는 클래스 인스턴스를 초기화할 수 있는 유연성
을 제공한다.
- 데이터 클래스는 컴파일러에서 equals, hashcode, toString, copy 및 기타 메서드를 제공한다.
- 클래스 위임은 코드에서 유사한 많은 위임 메서드를 피하는 데 도움이 된다.
- 객체 선언은 싱글톤 클래스를 정의하는 `Kotlin`의 방식이다.
- 컴패니언 객체는 `Java`의 `static` 메서드 및 필드 정의를 대체한다.
- 컴패니언 객체는 다른 객체와 마찬가지로 인터페이스를 구현할 수 있을 뿐만 아니라 확장 함수 및 프로퍼티를 가질 수 있다.
- 객체 표현식은 `Java`의 익명 내부 클래스를 대체하는 `Kotlin`의 기능으로, 여러 인터페이스를 구현하고 객체가 생성되는 범위에서 정의된 변수를 수정할 수 있는 등의 기능이 추가되어 있다.
- 인라인 클래스를 사용하면 수명이 짧은 객체를 많이 할당하여 발생할 수 있는 성능 저하를 방지하면서 프로그램에 유형 안전 계층을 도입할 수 있다.