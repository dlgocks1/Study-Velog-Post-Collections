> Kotlin In Action은 2017년도에 만들어진 책으로 내용이 오래되었고 친절하지 않는다. 수많은 내용이 있지만 나에게 기억이 남으면 좋을 내용들을 정리해 보았다.

# 1. 코틀린이란?

* 타입 추론을 지원하는 정적 타입 지정언어이다. 소스코드의 정확성과 성능을 보장하며, 소스코드를 간결하게 유지한다.

* 객체지향과 함수형 프로그래밍 스타일을 모두 지원한다.

* 실용적이며, 안전하고, 간결하며, 상호운용성이 좋다. `NullPointerException`과 같은 흔히 발생하는 오류를 방지하며, 읽기 쉽고 간결한 코드를 지원하면서 자바와 아무런 제약 없이 통합될 수 있다.

# 2. 코틀린 기초

* `val`, `var`은 각각 읽기 전용 변수와 변경 가능한 변수를 선언할 때 사용한다.

* 문자열 템플릿을 활용하자.

* 코틀린의 `when`은 자바의 `switch`보다 간결하고 강력하다.

* 한번 변수의 타입을 검사하면 이후 캐스팅이 필요가 없다.(스마트캐스팅)

* `1..5`와 같은 식은 범위를 만들어낸다. 범위에 들어있는지 검사하기 위해 `in`이나 `!in`을 활용한다.

* 코틀린은 프로퍼티를 언어 기본 기능으로 제공하며, 게터와 세터를 자동으로 구현한다.
	또한 커스텀 접근자를 수정할 수도 있다. 	
    
# 3. 함수 정의와 호출


* 이름있는 아규먼트를 활용하자

* 디폴트 파라미터 값을 활용하자

* 코틀린은 자신만의 컬렉션을 제공하지 않는다.
```
println(set.javaclass) // class java.util.Hashset

println(list.javaclass) // class java.util.ArrayList

println(map.javaclass) // class java.util.HashMap

println(MutableList(1) { 0 }.javaClass) // class java.util.ArrayList

println(Array(1) { 0 }.javaClass) // class [Ljava.lang.Integer;
```

모두 자바 컬렉션으로 이루어져 있으며 이는 자신만의 컬렉션을 제공하지 않는다는 뜻이다

하지만 `last()`, `first()`, `filter`등과 같은 컬렉션 API를 제공한다. 그 이유는 확장함수이다.

## 확장 함수

자바 컬렉션에 대한 확장함수를 선언하여 코틀린만의 컬렉션 선언없이도 여러 API를 제공한다.

```
// 확장함수의 예
fun String.lastChar(): Char = this.get(this.length - 1)
```

확장함수는 멤버 메소드인 것 처럼 호출하지만, 클래스 밖에 선언된 함수이다. 확장 함수를 만들기 위해서는 확장할 클래스의 이름을 덧붙이기만 하면된다.

* String -> `수신 객체 타입`
* this -> `수신 객체`

`String`클래스를 직접 작성하지 않고, 소스코드를 보유하지도 않았지만 원하는 메소드를 해당 클래스에 추가할 수 있다! 

> 확장함수를 남발하여 이름이 겹치지 않게 조심하자.
이름을 바꿔 임포트하거나, 전체 이름을 사용할 수 있지만 이는 좋은 방법이 아니다.

```
public fun <T> List<T>.last(): T { // 확장함수로 리스트에 API를 덧붙이고 있다.
    if (isEmpty())
        throw NoSuchElementException("List is empty.")
    return this[lastIndex]
}
```

### 확장함수는 오버라이드 불가능

확장함수는 오버라이드가 불가능하다. 이것이 무슨뜻이냐면
```
open class View {
	open fun click = println("Im View!")
}

class Button: View() {
	overrid fun click() = println("Im Button!")
}
```
다음과 같은 클래스가 있을 때 
```
View().click() // Im View!
Button().click() // Im Button!

val view: View = Button()
view.click() // Im Button!
```
함수가 오버라이딩되는 것은 당연하다.

하지만 확장함수는 클래스의 일부가 아니다. 클래스 밖에 선언되는 확장함수의 특성상 이런 오버라이드가 허용되지 않는다. 수신 객체로 지정한 변수의 정적 타입에 의해 어떤 확장함수가 호추로딜지 결정된다. (동적 타입에 확장함수가 의존하지 않음)

```
fun View.showOff() = println("Im a View!")
fun Button.showOff() = println("im a Button!")

val view: View = Button()
view.click() // Im View!
```



---

## 최상위 함수

자바에서는 모든 함수를 클래스의 메소드로 작성해야 한다. 하지만 이로 인해 중복된 일을 수행하는 클래스내 함수가 겹칠 수 있고, 많이 사용되지 않는 API를 위해 크기를 늘리는 일이 있을 수도 있다. 

> 코틀린은 이런 무의미한 클래스가 필요없다. 함수를 최상위 수준에 위치시키면 이 함수를 언제 어디서나 임포트하여 사용할 수 있기 때문이다.

```
fun joinToString() { /* .. */ }
```

코틀린은 JVM기반으로 돌아가는데 어떻게 이게 가능할까? 디컴파일해보자.

```
// In Join.kt
fun joinToString() {
    println("Hello!")
}

// Decompile
public final class JoinKt {
   public static final void joinToString() {
      String var0 = "Hello!";
      System.out.println(var0);
   }
```
최상위 함수를 디컴파일할 때 해당 소스가 있는 파일이름을 기반으로 새로운 클래스를 정의한다. 코틀린의 모든 최상위 함수는 이 클래스의 정적인 메소드가 된다. 즉 임포트하여 사용할 수 있다는 것 
```
JoinKt.joinToString() // 사용가능
```

---

## 최상위 프로퍼티

코틀린에서는 프로퍼티도 파일의 최상위 수준에 놓을 수 있다. 또 디컴파일 해보자.
```
// In Join.kt
private val imTopProperty = "Hello!"

// Decompile
public final class JoinKt {
   private static final String imTopProperty;

   static {
      imTopProperty = "Hello!";
   }
}
```
최상위 함수와 동일하게 `JoinKt`클래스의 변수로 사용되는 것을 볼 수 있다. 또한 이런 프로퍼티는 `static`으로 정적필드에 저장되며, `const val`한정자를 붙여 

`private static final String imTopProperty = "Hello!";`

public static final 필드로 컴파일하게 만들 수 있다.


## 가변 길이 인자, 중위 함수 호출, 라이브러리 지원에 대해서


###  `varage` 키워드를 사용하면 호출 시 인자 개수가 달라질 수 있는 함수를 정의할 수 있다.
```
val list = listOf(1, 2, 3, 4, 5, 6)
```

리스트는 생성할 때 원하는 만큼 많이 원소를 전달할 수 있다.
라이브러리에서 이 함수의 정의를 보면 다음과 같다.

```
fun listOf<T>(vararg values: T): List<T> { /* .. */}
```

자바스크립트의 스프레드 연산자(`...`)와 동일한 역할을 수행할려면 `*`을 앞에 붙여주면 된다.
```
val list = listOf("args: ", *args)
```

### 중위 `infix`함수 호출 구문을 사용하면 인자가 하나뿐인 메소드를 간편하게 호출할 수 있다.

[infix 함수에 대해](https://velog.io/@cksgodl/kotlin-kotlin%EC%97%90%EC%84%9C%EC%9D%98-infix-%EB%B0%8F-Builder-%ED%8C%A8%ED%84%B4)서는 이미 한번 다룬적이 있다.

>Infix 함수는 두개의 변수 가운데 오는 함수를 의미한다.
코틀린에서 기본적으로 정의된 Infix 함수들 중에 Pair를 만드는 to가 있다.

```
val pair = 'A' to 'B' // Pair("A", "B")
or
val pair = "A".to("B") // Pair("A", "B")
```

인자가 하나뿐인 확장 함수에 중위 호출을 사용할 수 있으며, 이는 함수 앞에 `infix`태그를 붙여 선언할 수 있다.

```
infix fun Any.to(other: Any) Pair(this, other)
```


### 자바스크립트와 같은 구조분해 선언을 제공한다.

`Pair`, `Map`, `List`와 같은 콜렉션에 대하여 코틀린은 구조분해 선언을 제공한다.

```
val (name, age) = Pair("해찬", 25)
val (num1, num2) = readLine()!!.split(" ").map { it.toInt() }
val (key, value) = mapOf(1, "value")
```

`for`와 같은 루프문에서도 이런 구조분해 선언을 활용할 수 있다. 각각의 콜렉션을 분해할 때 잘 사용하자.

```
for ((index, element) in collection.withIndex()) {
	println("$index : $element")
}
```

## 정규식을 사용할때는 3중 따음표(""")를 활용하자


```
val regex = """(.+)/(.+)\.(.)""".toRegex()
```

해당 3중 따음표를 활용하면 이스케이프 문자를 활용할 필요 없이 정규식을 복붙할 수 있다.


## 로컬 함수를 활용해보아라

```
fun saveUser(user: User) { 
	fun validate(user: User, value: Value) {
    	// Do Validate
    }
    validate(user, user.name)
    validate(user, user.pw)
}
```
함수 내에 함수를 적용할 수 있다. 로컬 함수는 자신이 속한 바깥함수의 모든 파라미터와 변수를 사용할 수 있다. 이를 활용하여 가독성 높은 코드를 작성하라

## 정리 

* 코틀린은 자체 컬렉션 클래스를 정의하지 않고 자바 클래스에 확장함수를 덧붙여 기능을 제공한다.

* 아규먼트에 대한 디폴트 값, 이름있는 아규먼트를 활용하여 개발자가 함수를 사용하게 쉽게 만들어라.

* 주로 사용되는 함수는 최상위 함수 및 프로퍼티로 추출하고 중복을 조심하라

* 외부 라이브러리에 대한 추가적인 API가 필요할 땐 확장함수를 활용하여 기능을 확장하라

* 인자가 하나밖에 없는 메소드나 확장 함수면 `infix`를 고려하라

* 정규식은 3중 따음표를 사용해라

* 함수내의 함수 즉 로컬함수를 활용하여 코드 중복을 줄이며 코드를 가독성 좋게 유지하라


# 4. 클래스, 객체, 인터페이스 🚌


코틀린에서 인터페이스를 상속받는 클래스는 무조건 인터페이스에 정의된 메소드를 오버라이딩 해야한다. (`super.mothod()`라도 작성해야함) 그렇지 않으면 컴파일 오류가 발생하게 된다.

또한 클래스는 단 하나의 클래스밖에 상속받지 못하며, 인터페이스는 여러개 상속받을 수 있다. 

## 상속은 위험하다.

`Effective Java`에서 상속을 위한 설계와 문서를 갖추거나, 그럴 수 없다면 상속을 금지하라. 라는 조언을 한다. 이는 특별히 하위 클래스에서 오버라이드하게 의도된 클래스와 메소드가 아니라면 모두 `final`로 만들라는 뜻이다. 

코트린도 마찬가지 철학을 따른다. 상속을 허용하려면 클래스 앞에 `open`변경자를 붙여야 하며, 그와 더불어 오버라이드를 허용하고 싶은 메소드나 프로퍼티 앞에도 `open`변경자를 붙여야 한다. (단 추상클래스는 붙이지 않아도 된다.)

추상클래스는 프로퍼티와 메소드를 모두 직접구현하여 전달할 수 있고, [인터페이스와는 다음과 같은 차이가 있다.](https://velog.io/@cksgodl/Kotlin-Abstract-class%EC%99%80-interface%EC%9D%98-%EC%B0%A8%EC%9D%B4-%EB%AC%B4%EC%97%87%EC%9D%84-%EC%8D%A8%EC%95%BC-%ED%95%A0%EA%B9%8C)
```
abstract class AbstractTest(){

    var a:Int = 0
        get() = b
        set(value) {
            field = value
        }

    val b:Int = 1

    fun doSomething() {
        a += 5
    }
}
```

```
open class OpenTest(): SomeInterface {
	fun sayHello() {} 		// 함수가 Final로 선언된다.
    open fun sayBye() {}	// 오버라이드 가능
    override fun inroduce() {} // 오버라이드 된 메소드는 기본적으로 open이다.
}
```

추상 클래스와 인터페이스에도 `final`을 붙여서 오버라이드를 금지할 수 있다.





## 가시성 변경자에 대하여


코틀린의 가시성 변경자는 자바와 비슷하다.

* public

* protected

* private

아무 변경자도 없을경우는 `public`으로 선언된다.

패키지 전용 가시성에 대한 대안으로는 코틀린에서 `internal`이라는 새로운 가시성 변경자를 도입했다.(모듈 내부

코틀린에서는 최상위 선언에 대해 `private` 가시성을 허용한다. 그런 최상위 선언에는 클래스, 함수, 프로퍼티가 적용 가능하며, 파일 내부에서만 사용할 수 있다.

> 짦은 상식

코틀린의 `interval` 변경자는 자바의 바이트코드로 디컴파일하면 `public`이 된다. 이는 패키지 전용 가시성이 자바에서 존재하지 않기 때문이다. 이러한 `public`으로 바뀌어진 `interval` 멤버는 컴파일러에 의해 멤버 이름이 바뀌게되며 이는 우연히 같은 메소드가 중첩되거나, 실수로 모듈 외부에서 사용하는 것을 막기 위함이다.

## 중첩 클래스에 대해

중첩 클래스는 바깥쪽 클래스에 대한 참조를 하지 않는다. 바깥 클래스 참조를 위해서는 `inner` 한정자를 붙여 사용하자

```
class A() {

	class B() // A에 대한 참조 불가능
}

class C() {

	class D() {
    	this@C // C에 대한 참조 가능
    }
}
```

## Sealed 클래스에 대해

중첩 클래스에는 중첩의 제한이 존재하지 않는다. 클래스 계층을 제한하려면 `Sealed Class`를 활용하자. 상위 클래스에 `sealed` 변경자를 붙이면 그 상위 클래스를 상속한 하위 클래스를 제한할 수 있다. (when 문을 활용할 때 `else`브런치를 쓸 일이 없다.)

다음은 음식 카테고리를 제한하여 나누는 `Sealed Class`다. 
```
enum class FoodCategory(
    private val categoryName: String,
    private val menus: List<String>
) {
    KOREAN(KR_KOREAN, KOREAN_FOODS),
    JAPANENSE(KR_JAPANESE, JAPANESE_FOODS),
    CHINESE(KR_CHINESE, CHINESE_FOODS),
    ASIAN(KR_ASIAN, ASIAN_FOODS),
    WESTERN(KR_WESTERN, WESTERN_FOODS);
}    
```

`sealed`로 표시된 클래스는 자동으로 `open`이 된다.


## object 키워드에 대해

#### object 키워드 란
* 객체 선언은 싱글턴을 정의하는 방법 중 하나이다.

* `Companion Object`는 인스턴스 메소드는 아니지만, 어떤 클래스와 관련 있는 메소드와 팩토리 메소드를 담을 때 쓰인다. 

* 객체 시근 자바의 무명 내부 클래스(anonumous inner class) 대신 쓰인다.

코틀린은 obejct 선언을 통해 싱글톤을 기본적으로 지원한다. (단일 인스턴스) 
```
object Payroll {
	val allEmployees = arrayListOf<Person>()
    
    fun calculateSalary() {
    	// ...
    }
}
```

클래스를 정의하고 인스턴트를 만드는 모든 작업이 한줄로 처리된다. 이는 클래스와 동일하게 메소드, 초기화 블록 등이 들어갈 수 있다. **하지만 생성자는 객체 선언에 사용할 수 없다.** 싱글톤 객체는 생성자 호출 없이 즉시 만들어진다.

이러한 싱글톤 `object`도 클래스나 인터페이스를 상속할 수 있다. 또한 `object`내에 객체를 선언할 수도 있으며 이역시 인스턴스는 단 하나뿐이다. 

### 동반 객체에 대하여

코틀린은 클래스 내부에 정적인 멤버가 없다(static 선언이 불가능) `private`으로 표시된 클래스의 비공개 멤버에 접근할 수 없다. 그러므로 클래스의 인스턴스와 상관없이 호출해야 하지만, 클래스 내부 정보에 접근해야 하는 함수가 필요할 때는 클래스에 중첩된 객체 선언의 멤버 함수로 정의해야 한다. 대표적인 예로는 팩토리 메소드가 있다.

[생성자 대신 팩토리 함수를 사용하여라](https://velog.io/@cksgodl/Kotlin-%EC%83%9D%EC%84%B1%EC%9E%90-%EB%8C%80%EC%8B%A0-%ED%8C%A9%ED%86%A0%EB%A6%AC-%ED%95%A8%EC%88%98%EB%A5%BC-%EC%82%AC%EC%9A%A9%ED%95%98%EB%9D%BC)에서 보았듯이 동반객체를 활용한 생성자는 간단하고 편리하다. 

동반객체는 바깥족 클래스의 private한 생성자도 호출할 수 있다. 

```
class User private constructor(val nickname: String) {
	companion object {
    	fun newSubscribingUser(email: String) = 
        	User(email.substringBefore('@')
        fun newFacebookUser(accuntId: Int) =
        	User(getFacebookName(accountId)
    }
}
```

이러한 팩토리 메소드는 생성할 필요가 없는 객체를 생성하지 않을 수 있다. 예를 들어 이메일 주소별로 유일한 `User` 인스턴스를 만드는 경우 팩토리 메소드가 이미 존재하는 인스턴스에 해당하는 이메일 주소를 전달받으면 새 인스턴스를 만들지 않고 캐시에 있는 기존 인스턴스를 반환할 수 있다. 

#### 동반 객체도 객체야 객체

동반 객체는 클래스 안에 정의된 일반 객체이다. 따라 동반 객체에 이름을 붙이거나, 동반 객체가 인터페이스를 상속하거나, 동반 객체 안에 확장 함수와 프로퍼티를 정의할 수 있다.

```
class Person(val name: String) {
	companion object Loader : JSONFactory<Person> {
    	override fun fromJSON(jsonText: String): Person {
        	// Dd shomething!
        }
    }
}

Person.Loader.fromJSON("JSON TEXT")
```

특별한 이름을 지정하지 않으면 자동으로 `Companion`이 된다. 

또한 동반 객체도 객체이기 때문에 확장함수를 정의할 수 있다.

```
fun Person.Loader.fromXML(xmlString: String) : Person {
	// Person
}
```
동반객체에 대한 확장 함수를 작성하고자 한다면 빈 객체라도 동반 객체를 꼭 선언하자.


## object 식에 대해 -> 무명 내부 클래스를 다른 방식으로 작성


object 키워드를 싱글턴과 같은 객체를 정의하고 그 객체에 이름을 붙일 때만 사용하지는 않는다.`무명 객체`를 정의할 때도 `object`키워드를 쓴다. 무명 객체는 자바의 무명 내부 클래스를 대신한다. 다음과 같은 이벤트 리스너를 보자

```
window.addMouseListener {
	object : MouseAdaptor() {
    	override fun mouseClicked(e: MouseEvent) {
        	// ...
        }
        
        override fun mouseEntered(e: MouseEvent) {
        	// ...
        }
    }
}
```

사용한 구문은 객체 선언에서와 같다. 한 가지 유일한 차이점은 객체 이름이 빠졌다는 점이다. 객체 식은 클래스를 정의하고 그 클래스에 속한 인스턴스를 생성하지만, 그 클래스나 인스턴스에 이름을 붙이지는 않는다. 

> 이러한 무명 객체는 싱글턴이 아니다. 객체 식이 쓰일때마다 새로운 인스턴스가 생성된다.

구현해야할 함수가 하나뿐인 무명객체를 `SAM`이라고 하며 코틀린에서는 이를 람다로 변환하여 사용할 수 있다.

## 정리

* 코틀린의 인터페이스는 자바 인터페이스와 비슷하지만 디폴트 구현을 포함할 수 있고, 프로퍼티도 포함할 수 있다. (게터와 세터를 인터페이스 내부에서 구현하고, 상속받은 클래스가 해당 프로퍼티를 변경하고자 할 때 오류가 발생할 수 있으먜

* 모든 코틀린 선언은 기본적으로 `final`이며 `public`이다.

* 선언이 `final`이 되지 않게 하려면 `open`을 붙여라

* `internal`선언은 같은 모듈 내에서만 사용이 가능하다.

* 중첩 클래스는 기본적으로 내부 클래스가 아니다. 바깥 클래스에 대한 참조를 포함시키려면 `inner`한정자를 붙여라

* `field` 식별자를 통해 프로퍼티 접근자 안에서 프로퍼티의 데이터를 저장하는 데 쓰이는 뒷받침 필드를 참조할 수 있다.

* 데이터 클래스를 활용하면 `equals`, `hashCode`, `toString`, `copy`등 메소드를 자동으로 생성해 준다. (데이터 클래스의 `==`는 내부 프로퍼티의 값에 의해 결정된다.)

* 클래스를 위임을 사용하면 위임 패턴을 구현할 때 적을 수많은 메소드 코드를 줄일 수 있다. [위임을 통한 일급콜렉션은 사용하지 말자](https://velog.io/@cksgodl/Kotlin-%EC%BD%94%ED%8B%80%EB%A6%B0%EC%97%90%EC%84%9C-%EC%9D%BC%EA%B8%89-%EC%BD%9C%EB%A0%89%EC%85%98%EC%9D%80-%ED%95%84%EC%9A%94-%EC%97%86%EB%8B%A4)

* `object`선언을 사용하면 코틀린답게 싱글턴 클래스를 정의할 수 있다.

* 동반 객체도 다른 객체와 마찬가지로 인터페이스를 구현할 수 있다. 또한 외부에서 동반 객체에 대한 확장함수 및 프로퍼티를 정의할 수 있다.

* 코틀린의 객체 식은 자바의 무명 내부 클래스를 대신한다. 하지만 코틀린 객체식은 여러 인스턴스를 구현하거나 객체가 포함된 영역 있는 변수의 값을 변경할 수 있는 등 자바 무명 내부 클래스보다 많은 기능을 제공한다.
 
---

# 5. 람다로 프로그래밍

> 람다란? 다른 함수에 넘길 수 있는 함수를 의미한다.

## 람다 식과 멤버 참조

과거 자바프로그래머들은 람다의 도입을 오랫동안 기다려왔고, 자바 8에서의 람다의 도입은 그 기다림의 끝이었다. 람다가 뭐길래 이랬을까?

### 코드 블록을 함수 인자로 넘길 수 있다.

```
A 이벤트가 발생하면 B에게 어떤 연산을 수행하고 C를 반환하자.
```
라는 이벤트가 있을 때 이 행동을 코드로 구현하기 위해 동작을 함수에 넘겨야 할 경우가 자주 있다. 자바에서는 무명 내부 클래스를 통해 이런 목적을 달성했다. 하지만 무명 내부 클래스를 활용하는 것은 상당히 번거롭다.

함수형 프로그래밍에서는 함수를 값처럼 다루는 접근 방법을 택함으로 이 문제를 해결한다. 람다 식을 활용하여 함수를 직접 함수로 넘길 수 있으며 이를 콜백함수라고 칭하기도 한다.


자바 에서의 `onClickListener`는 무명 내부 클래스의 대표적인 예이며 코드가 번잡스러움을 느낄 수 있다.
```
button.setOnClickListener(new OnClickListneer() {
	@Override
    public void onClick(View view) {
    	// 클릭 시 동작 수행
    }
}
```

코틀린은 이러한 무명 내부 클래스(`SAM`)을 람다 식으로 대치할 수 있다. 이는 더 간결하고 읽기 쉽다.

```
button.setOnClickListner { /* 클릭 시 수행할 동작 */ }
```

### 람다 식의 문법

람다를 따로 선언하여 변수에 저장할 수도 있다. 또한 람다 식은 인자를 가질 수 있다.

```
val sum = { x:Int, y:Int -> x + y }
print(sum(1, 2)) // 3
```

코틀린의 람다 식은 화살표`->`를 이용해 인자와 람다 본문을 구별한다.

람다 식은 일반 함수와 동일하게 직접 호출도 가능하다.
```
{ print(42) }()
```
하지만 이런 구문은 읽기 어렵고 쓸모도 없다. 람다를 만들자마자 실행할 이유가 없기에 이러한 코드는 `run`을 활용한다.

`run`은 인자로 받은 람다를 바로 실행해주는 함수이다.
```
run { print(42) }
```

실행 시점에 코틀린의 람다 호출에는 아무 부가 비용이 들지 않으며, 프로그램의 기본 구성요소와 비슷한 성능을 낸다. 

```
people.maxBy({ p: Person -> p.age })
```

콜렉션의 확장함수 `maxBy`는 람다 식을 인자로 받고 람다 식은 `Person`타입의 값을 인자로 받아 인자의 `age`를 반환한다.

코틀린에 익숙한 개발자는 다음 함수가 번잡하다는 것을 바로 알 수 있을 것이다. 우리는 다음과 같은 과정을 거쳐 람다식을 최소화한다.

1. 컴파일러가 유추할 수 있는 인자 타입을 생략한다
2. 마지막 인자인 람다식을 괄호 밖으로 추출한다.
3. 람다의 파라미터가 하나뿐이고 그 타입을 컴파일러가 추론함으로 `it`으로 바꾸어 사용한다.


```
people.maxBy { it.age }
```

> `it`의 남용은 위험하다. 람다와 람다가 중첩되는 경우, 파라미터 이름을 지정하여 사용하도록 하자.

여러줄의 람다식은 본문의 맨 마지막에 있는 식이 람다의 결과 값이 된다.(`return`을 사용하지 않음)

```
val sum { x: Int, y: Int -> 
	println("Computing the sum of $x and $y...")
    x + y // 결과 값
}
```

### 현재 영역에 있는 변수에 접근하기

람다를 함수 내부에서 정의하면 함수의 파라미터뿐 아니라 람다 정의의 앞에 선언된 로컬 변수까지 람다에서 모두 사용할 수 있다.

```
fun someFunction(people: List<String>, name: String, age: Int) {
	people.forEach {
    	if(name == it) {
    		println("$age인 $name을 찾았다.")         
        }
    }
}
```
람다 내부에서 바깥의 변수를 변경할 수도 있다. 이런 람다 안에서 사용되는 외부 변수를 `람다가 포획한 변수`라고 부른다. 

> 기본적으로 함수 안에 정의된 로컬 변수의 생명주기는 함수가 반환되면 끝난다. 하지만 어떤 함수가 자신의 로컬 변수를 포획한 람다를 반환하거나 다른 변수에 저장한다면 로컬 변수의 생명주기와 함수의 생명주기가 달라질 수 있다.

람다가 `var`변수를 포획하면 변수를 `Ref`클래스 인스턴스에 넣는다. 그 `Ref` 인스턴스에 대한 참조를 파이널로 바꾸어 람다를 포학하고, 람다 식 내부에서 `Ref` 인스턴스에 대한 필드를 변경한다.

람다를 이벤트 핸들러나 비동기적으로 실행되는 코드로 활용할 경우 함수 호출이 끝난 후 로컬 변수가 변경될 수 있다.

```
fun tryToCountButtonClicks(button: Button) : Int {
	var clicks = 0
    button.onClick { clicks++ }
    return clicks
}
```

해당 함수는 무조건 0을 반환한다. 람다 식이 증가 시키기전에 함수를 반환하기 때문이다.


## 멤버 참조

코틀린은 자바 8과 마찬가지로 함수를 값으로 바꿀 수 있따 이때 `이중 콜론(::)`을 사용한다.

```
val getAge = Person::age
```

> 이를 `멤버 참조`라고 부른다. 멤버 참조는 프로퍼티나 메소드를 단 하나만 호출하는 함수 값을 만들어 준다.

`Person::age`는 다음 람다 식을 간략하게 표현한 것이다.

```
val getAge = { person: Person -> person.age }
```

멤버 참조 뒤에는 괄호를 넣으면 안된다. 멤버 참조는 그 멤버를 호출하는 람다와 같은 타입이다. 따라서 다음 예처럼 그 둘을 자유롭게 바꿔 쓸 수 있다.

* `people.maxBy(Person::age)`
* `people.maxBy { p -> p.age }`
* `people.maxBy { it.age }`

람다가 인자가 여럿인 다른 함수한테 작업을 위임하는 경우 람다를 새로 정의하지 않고 직접 위임 함수에 대한 참조를 제공하면 편리하다.

```
val action = { person: Person, message: String -> 
	sendEmail(person, message)
}
val nextAction == ::sendEmail
```

## 컬렉션 함수형 API 🤔

나이가 가장 많은 사람의 리스트가 필요하다고 해보자.
```
people.filter { it.age == people.maxBy(Person::age)!!.age }
```
한 줄로 간단하게 표현할 수 있겠지만, 해당 코드에서는 최갯값을 구하는 작업을 계속 반복한다. 그러므로 이를 좀 더 개선해 최댓값을 한 번만 계산하게 만들자.

```
val maxAge = people.maxBy {Person::age}!!.age
people.filter { it.age == maxAge }
```

항상 작성하는 코드가 어떻게 계산되는지 명확하게 이해하자.

### 술어 함수에 대해

```
val canBeInClub27 = { p: Person -> p.age <= 27}
```
다음은 술어 함수의 예이다. 이를 활용한 예를 보자.
```
people.all(canBeInClub27)) // 모든 사람이 27살 이하인지
people.any(canBeInClub27)) // 27살 이하인 사람이 있는지
people.count(canBeInClub27)) // 27살 이하의 수 
people.find(canBeInClub27)) // 27살 이하인 사람 찾기
```

다음과 같이 술어 함수에 대한 콜레션 `API`는 정말 다양하게 제공된다. 같은 조건을 여러번 적용해야한다면 술어 함수로 추출하여 사용하자.

### groupBy : 리스트를 여러 그룹으로 이루어진 맵으로 변경🤽‍♂️

```
people.groupBy { it.age }
```

다음은 나이를 키값으로 리스트를 맵으로 바꾸어준다.

```
{
	29 = [Person(name=Bob, age=29)],
    31 = [Person(name=Alice, age=31), Person(name=Carol, age=31)]
}
```

각 그룹은 리스트다. 따라서 `groupBy`의 결과 타입은 `Map<Int, List<Person>>`이다. 


## 수신 객체 지정 람다 `with`와 `apply`

지역 스코프 함수라고 불리기도 하는 이 두 함수는 편리하며, 많이 사용된다. 이는 코틀린 람다에서 수신 객체를 명시하지 않고 람다의 본문 안에서 다른 객체의 메소드를 호출할 수 있게 하는 것이다. `수신 객체 람다`에 대해 자세히 알아보자.

### with

코드절이 어떤 객체의 이름이 반복될 때, `with`를 사용해보자.

```
fun alphabet() : String {
    val result = StringBuilder()
    for (letter in 'A'..'Z'){
        result.append(letter)
    }
    result.append("\n알파벳 다 모았다~")
    return result.toString()
}
```

`result`를 몇번 사용했을까? 위의 예에서는 3번 중복으로 사용됬다.

이를 `with`를 활용하여 리팩토링해보자.
```
fun alphabet() : String = with(StringBuilder()){
    for (letter in 'A'..'Z'){
        this.append(letter)
    }
    this.append("\n알파벳 다 모았다~")
    this.toString()
}
```

`with`내부에서는 `this`를 활용해 그 인스턴스를 참조할 수 있다. 만약 수신 지정 객체 람다가 겹치면`this@with`와 같이 @를 붙여서 특정 수신 객체를 지정할 수 있다.

```
@kotlin.internal.InlineOnly
public inline fun <T, R> with(receiver: T, block: T.() -> R): R {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    return receiver.block()
}
```

정의에서도 볼 수 있듯이 `with`는 수신 객체 지정 람다가 실행한 결과값을 반환한다. 그렇다면 `apply`는 어떨까?

### apply

```
@kotlin.internal.InlineOnly
public inline fun <T> T.apply(block: T.() -> Unit): T {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    block()
    return this
}
```
`apply`는 `with`와 거의 비슷하지만, 수신 객체를 직접 반환된다. 이를 활용하여 `alphabet`함수를 다시 만들어보자.

```
fun alphabet() : String = StringBuilder().apply {
    for (letter in 'A'..'Z'){
        append(letter)
    }
    append("\n알파벳 다 모았다~")
}.toString()
```

수신객체 그 자체를 반환하기에 마지막에 `toString()`으로 변환하여 반환함을 볼 수 있다. 이는 어떤 객체에 대하여 내부 값을 많이 변경해야할 때 유용하다.

```
val someObject = TextObject().apply {
	text = "제목"
    textSize = ...
    textColor = ...
    textAlign = ...
}
```
`apply`는 인스턴스를 만들고 인스턴스 내부 값을 변경한 결과 값을 반환한다.


## 정리

* 람다를 사용하면 코드 조각(동작)을 다른 함수에게 인자로 넘길 수 있다.

* 코틀린에서는 람다가 함수 인자인 경우 괄호 밖으로 람다를 뺄 수 있고, 람다 인자가 하나뿐일 경우 `it`을 활용할 수 있다.

* 람다 안에 있는 코드는 바깥 함수의 변수를 읽을 수 있다.(변수를 포획함)

* 메소드, 생성자, 프로퍼티의 이름 앞에`::`를 붙이면 각각에 대한 참조를 만들 수 있다. 이런 참조는 람다 대신 다른 함수에게 넘길 수 있다.

* 시퀀스를 활용하면 중간 결과로 리스트가 생기지 않으며 `lazy`한 연산이 수행된다. 크기가 큰 컬렉션을 처리하거나, 몇개의 결과 값만 필요할 때 활용하자.

* `SAM`을 인자로 받는 함수를 호출할 경우 람다를 넘길 수 있다.

* 수신 객체 지정 람다를 활용하여 중복을 없애고, 수신 객체의 메소드를 직접 호출할 수 있다.


# 코틀린 타입 시스템

1. 널이 될 수 있는 타입과 널을 처리하는 방법
2. 코틀린 원시 타입, 자바 타입과 코틀린 원시 타입의 관계
3. 코틀린의 컬렉션 소개와 자바 컬렉션과 코틀린 컬렉션의 관계

## 코틀린은 Null값을 허용하지 않는다.

`nullablity`는 런타임 때 정말 많은 오류를 낸다. 코틀린은 이를 런타임까지 가지 않고, 컴파일 시점에서 체크하고자 `Null`값을 허용하지 않는 자료형을 활용한다. `Java`는 모든 변수가 `Nullable`인데 어떻게 호환되는지도 알아보자.

### 널이 될 수 있는 타입

코틀린은 `?`를 붙여서 `nullable`타입을 정의한다.
```
val nullableInt : Int? = 0
val nullableString : String? = null
val nullableBoolean : Boolean? = false
```
이러한 변수를 활용할 때는 `null`체크를 하지 않으면 컴파일러가 에러를 뱉어낸다.
`if(nullableInt != null) { do Something }`과 같이 `if`문을 활용하여 `null`을 계속 체크할 수 있겠지만 이는 효율적이지 않다.

좀 더 우아하게 `null`을 다룰 수 있는 방법을 알아보자.

### 안전한 호출 연산자 ?. , 엘비스 연산자 ?:

코틀린이 제공하는 가장 유용한 도구 중 하나가 바로 safe 연산자인 `?.`이다. 이는 해당 값이 `null`이 아니라면 작동하고, `null`이라면 건너뛴다. 

```
nullObject?.function() // 작동 X
notNullObejct?.function() // 작동 O
```

또한 이를 같이 활용한 `elvis(?:)`연산자도 유용하다.

`null` 대신 활용할 디폴트 값을 지정할 때 편리하게 사용할 수 있는 연산자를 제공하는데 이를 엘비스 연산자`(?:)`라고 한다. 
```
val title = nullableText ?: "Default Title"
```
`nullableText`가 `null`이 였다면 기본 제목이 `title`에 들어갈 것이다.

또한 `return`, `throw`등의 연산도 식이기 때문에 엘비스 연산자와 같이 활용될 수 있다.

### 안전한 캐스트: as?

`as`를 활용하여 타입캐스트를 진행할 수 있고, 만약 바꿀 수 없으면 `ClassCastException`이 발생하게 된다. `is` 연산자를 통해 변환 가능한 타입인지 일일이 체크할 수 있지만 이역시도 간결하지 않다.

> `as?`연산자는 어떤 값을 지정한 값으로 캐스팅하되, 할 수 없으면 `null`을 반환한다.

안전한 캐스트를 활용할 때 일반적인 패턴은 캐스트를 수행한 뒤, 엘비스 연산자를 활용하는 것이다.

```
class Person(val firstName: String, val lastName: String) {
	override fun equals(o: Any?): Boolean {
    	val otherPerson = o as ? Person ?: return false
        return other.firstName == firstName && 
        	other.lastName == lastName
    }
}
```

### 널이 아님을 단언: !!

`not-null assertion`은 단순하면서도 위험한 도구이다. 이는 널이 아닌 탙입으로 강제로 바꾸며 편리하지만 이를 남발하다가는 에러가 한번 났을 때 디버깅하기가 정말 어려울 것이다. 

```
person..company!!.address!!.country
```
다음과 같이 `!!`를 중복하여 사용하면 스택 트레이스에서 몇 번째 줄에서 에러가 났는지는 알려주지만, 어떤 결과 값이 `null`인지는 알려주지 않는다. 이런 식으로 코드를 작성하지 말자

### 간단하게 nullable값을 넘기자: let

`let`함수를 활용하면 널이 될 수 있는 식을 더 쉽게 다룰 수 있다. `let` 함수를 안전한 호출 연산자와 함께 사용하면 원하는 식을 널인지 검사한 후에 동작을 수행할 수 있다. 가장 간단하고 가독성이 좋은 연산자이기도 하다

```
email?.let { email -> sendEmailTo(email) } // 복잡한 null체크 구문이 없다.
```

또한 `let`을 활용하면 식의 결과를 저장하는 변수를 따로 만들 필요가 없다.

```
val person: Person? = getTheBestPersonInTheWorld()
if(person != null) sendEmailTo(person.email)

getTherBestPersonInTherWorld()?.let { sendEmailTo(it.email) }
```

### 나중에 초기화할 프로퍼티

코드를 작성하며 자바의 코드를 코틀린으로 자동으로 바꿀 때는 다음과 같은 소스를 많이 보았을 것이다.

```
private sumVar : String? = null
```

자바는 모든 변수가 null이 될 수 있음으로 코틀린에서 이를 복사하면 `nullable`프로퍼티로 자동으로 바꾸어 사용한다. 하지만 이는 사용할 때마다 널 검사를 하거나 `!!`을 붙이는 등의 노력이 필요하다.

이를 해결하기 위해 프로퍼티를 `나중에 초기화`할 수 있다. `lateinit`

```
private lateinit var myService: Myservice

@Before
fun setUp() {
	myService = MyService()
}
```

`lateinit`초기화 프로퍼티는 항상 `var`이여야 하며, 초기화 하지 않은 채 사용하면 `lateinit property has not been initialized`가 발생한다. 이는 어디가 잘못됐는지 확실히 알려주며, `NullPointerEception`보다 더 깔끔하다.

#### nullable한 값에 대한 확장함수를 따로 제공한다

`isNullOrEmpty`나 `isNullOrBlank`와 같은 메소드는 null일 때를 고려하여 결과 값을 반환한다. 널체크를 따로 진행하지 않고 이런 확장함수를 직접 정의하여 사용할 수도 있다.

### 타입 파라미터(제너릭 T)의 널 가능성

코틀린의 함수나 클래스의 모든 타입 파라미터는 널이 될 수 있다. 널이 될 수 있는 타입을 포함하는 어떤 타입이라도 타입 파라미터를 대신할 수 있다.

```
fun <T> printHashCode(t: T) {
	println(t?.hashCode()) // T는 널일 수 있다.
}
```

`T`에 대한 타입 추론은 `Any?`타입이다. 파라미터의 타입 이름 `T`에는 물음표가 붙어있지 않지만 `T`는 `null`을 받을 수 있다. 이러한 타입 파라미터가 널이 아님을 확실히 하려면 널이 도리 수 없는 타입 상한(upper bound)를 지정해야 한다. 널이 될 수 없는 타입 상한을 지정하면 널이 될 수 있는 값을 거부한다.

```
fun <T:Any> printHashCode(t:T) {
	println(t.hashCode()) // T는 널이될 수 없다.
}
```
이와 같이 타입 파라미터는 널이 될 수 있는 타입을 표시하는 `?`에서 벗어나는 유일한 예이다.


## 널 가능성과 자바

코틀린은 상호운용이 뛰어난 언어이다. 하지만 자바에서는 모든 변수를 `nullable`로 처리하며 오류가 있을 것 같다. 코틀린과 타 언어끼리 소통을할 때 코틀린은 어떻게 해야할까?

### 플랫폼 타입

플랫폼 타입은 코틀린이 널 관련 정보를 알 수 없는 타입을 말한다. 그 타입을 널이 될 수 있는 타입으로 처리해도 되고, 널이 될 수 없는 타입으로 처리해도 된다. 

```
Java.String == Kotlin.String
Java.String == Kotlin.String?
```

코틀린은 보통 널이 될 수 없는 값에 대해 널 안전성 검사를 중복 수행해도 아무 경고도 표시하지 않는다. 어떤 플랫폼 타입의 값이 널이 될 수도 있음을 인지했다면 그 값을 활용하기 전 검사를 할 수 있다. 

 자바를 코틀린과 함께 사용할 때는 자바 코드에 @Nullable과 @NotNull 어노테이션을 붙여서 사용하길 권장한다고한다. 

다음은 `Effective Kotlin`에서 발췌한 내용이다.
#### [안정성을 위해 플랫폼타입의 사용을 자제하라](https://velog.io/@cksgodl/kotlin-%EC%95%88%EC%A0%95%EC%84%B1%EC%9D%84-%EC%9C%84%ED%95%B4-%EC%B5%9C%EB%8C%80%ED%95%9C-%ED%94%8C%EB%9E%AB%ED%8F%BC-%ED%83%80%EC%9E%85%EC%9D%84-%EC%82%AC%EC%9A%A9%ED%95%98%EC%A7%80-%EB%A7%90%EB%9D%BC)


> 플랫폼 타입 -> 타언어에서 전달되어서 nullable인지 아닌지 알 수 없는 타입을 의미한다.

플랫폼 타입은 String!처럼 ! 기호를 붙여서 표기한다. 이러한 노테이션이 직접적으로 코드에 나타나진 않는다.

```
val user1 = repo.user 		// User!
val user2 : User= repo.user // User
val user3 : User? = repo.user// User?
```

#### 코틀린 코드에서 플랫폼 타입을 최대한 빨리 제거하자.
```
public class JavaClass{
	public String getValue(){
    	return null;
    }
}

// 코틀린
fun statedType() {
	val value: String = JavaClass().value // Error!!
    println(value.length)
}

fun platformType() {
	val value = JavaClass().value
    println(value.length) // Error!!
}
```
두 상황 모두 NPE가 발생하지만, 오류 위치에서 차이가 있다.

statedType()에서는 값을 가져오는 위치에서 NPE가 발생한다. 이 위치에서 오류가 발생하면, null이 아니라고 예상을 했지만 null이 나온다는 것을 굉장히 쉽게 알 수 있다. 즉 코드 수정이 용이해진다.

platformType()에서는 값을 사용할 때 오류가 난다. 타입 검사기가 이를 검출할 수 없음으로 오류를 찾는 데 오랜 시간이 걸릴 것이다.


### 상속

코틀린에서 자바 메소드를 오버라이드할 때 그 메소드의 파라미터와 반환 타입을 `Nullable`로 처리할 지 `not-nullable`로 처리할 지 결정해야 한다. 다음과 같은 예를 보자.

```
interface StringProcessor {
	void process(String value);
}

class StringPrinter: StringProcessor {
	override fun process(value: String) {
    	println(value)
    }
}

class NullableStringPrinter: StringProcessor {
	override fun process(value: String?) {
    	value?.let {
        	println(it)
        }
    }
}
```

자바에서 상속을 받을 때 널 가능성을 제대로 처리하는 것은 중요하다. 자바코드에서의 `@NotNull`과 같은 어노테이션이 붙어있지 않다면 `nullable`로 받아서 처리하자.

### Null에 관한 정리

* safe call `?`, elvis `?:`, not-null assertion `!`등을 활용하여 코틀린 배우세어 널을 관리하자. 

* `nullable`한 자료형에 대한 확장함수가 따로 정의되어있는 것을 잊지말자(널 체크를 확장함수 내부로 집어 넣기)

* 제너릭`T`는 `?`를 붙이지 않아도 `null`이될 수 있다.

* `let`을 통해 간단하게 널 안전성을 검증할 수 ㅇ있다.



## 코틀린의 원시 타입


[코틀린과 자바의 원시 타입에 대하여](https://velog.io/@cksgodl/Kotlin-%ED%9A%A8%EC%9C%A8%EC%84%B1-Kolin%EA%B3%BC-Java%EC%9D%98-%EC%9B%90%EC%8B%9C-%ED%83%80%EC%9E%85-%EC%B0%B8%EC%A1%B0-%ED%83%80%EC%9E%85%EC%97%90-%EB%8C%80%ED%95%B4)에서 이미 다뤘던 내용들이다.




## 가변 콜렉션과 불변 콜렉션에 대하여

`List<String>`는 `MutableList<String>`는 모두 `Collection`객체의 하위 타입으로 다른 점은 `add`, `remove`와 같은 기능의 유무이다. 이러한 컬렉션들을 사용할 떄 염두에 둬야 할 점은 읽기 전용 컬렉션이라고 해서 꼭 변경 불가능한 컬렉션일 필요는 없다는 것이다.

읽기 전용 컬렉션이 가르키는 인스턴스가 변경 가능한 콜렉션의 참조일 수도 있기 때문이다. 

한 컬렉션을 사용하는 도중 병렬 실행으로 다른 컬렉션이 그 컬렉션의 인스턴스를 변경할 때는 `ConcurrentModificationException`이 발생하게 된다. 따라 읽기 전용 컬렉션이 항상 쓰레드에 대해 안전`thread safe`하지는 않다는 점을 명심해야 한다. 다중 스레드 환경에서 데이터를 다루는 경우 그 데이터를 적절히 동기화 하거나 동시 접근을 허용하는 데이터 구조를 활용해야 한다.

### 코틀린과 자바의 컬렉션

코틀린의 `Mutable`한 콜렉션은 자바의 변경 가능한 인터페이스 `java.util` 패키지에 있는 인터페이스를 모두 그대로 사용한다. 다만 읽기 전용 인터페이스는 변경할 수 있는 모든 요소가 빠져있다.

```
public inline fun <T> List(size: Int, init: (index: Int) -> T): List<T> = MutableList(size, init)
```

`List`는 변경이 불가능한 타입이지만 이를 만들 때는 변경 가능 클래스인 `MutableList`생성자를 활용하여 만든다. 즉 내부적으로 이들은 변경 가능한 클래스이다. (자바의 콜렉션을 기반으로 하기 때문에) 따라 `java.util.Collection`을 파라미터로 받는 자바 메소드가 있다면 `Mutable`이든 `Immutable`이든 아무런 값이나 인자로 넘길 수 있다.

이에 따라서 코틀린의 읽기 전용 콜렉션객체라도 자바 코드에서는 이를 변경할 수 있다.

```
fun printInUpperCase(list: List<String>) {
	println(CollectionUils.uppercaseAll(list))
    println(list.first())
}

val list = listOf("a", "b", "c")
printInUpperace(list) // [A, B, C]
```

컬렉션을 자바로 넘기는 코틀린 프로그램을 작성한다면 컬렉션을 변경할지 여부에 따라 콜렉션을 맞추어 보내주어야 한다.

이런 함정은 널이 아닌 원소로 이루어진 컬렉션 타입에도 해당된다. 자바 메소드에서는 널을 컬렉션에 넣을 수 있기 때문이다.

```
Kotin.List<Int> == Java.List<Int?>
```

### 컬렉션을 플랫폼 타입으로 다루기

자바에서는 콜렉션에 대한 수정이 자유롭다. (코틀린은 `Mutable`한 콜렉션만 가능) 따라 언어간의 콜렉션 통신이 필요할 때 다음을 고려해야 한다.

* 컬렉션이 널이 될 수 있는가?
* 컬렉션의 원소가 널이 될 수 있는가?
* 오버라이드하는 메소드가 컬렉션을 변경할 수 있는가?


### 객체의 배열과 원시 타입의 배열

코틀린의 배열은 타입 파라미터를 받는 클래스이다. 

```
arrayOf<Int>(1,2,3)
arrayOfNulls<Int?>(5)
Array(5) { 0 }
```

코틀린에서는 배열을 인자로 받는 자바 함수를 호출하거나, `vararg` 파라미터를 받는 코틀린 함수를 호출하기 위해 자주 배열을 만든다. 이 때 데이터가 이미 콜렉션이 들어가 있다면 컬렉션을 배열로 변환해야한다. `toTypedArray`메소드를 활용하면 쉽게 콜렉션을 배열로 바꿀 수 있다.

> 배열 타읩의 인자도 항상 참조 타입이다. 즉 `Array<Int>`는 자바에서 `java.lang.Integer[]`로 표현된다. 원시 타입의 배열이 필요하다면 그런 타입을 위한 특별한 배열클래스를 사용한다.


* IntArray
* ByteArray
* CharArray
* BooleanArray

등은 원시 타입 배열이다. 이들은 모두 자바에서 `int[]`, `byte[]` 등으로 컴파일 된다. 따라서 라이브러리와 같은 성능이 중요한 코드에서는 이러한 원시타입 배열을 사용하자. (이러한 원시 타입 배열도 콜렉션 API를 모두 제공한다!)

## 정리

* 코틀린은 널이 될 수 있는 타입을 지원해 `NullPointException`오류를 컴파일 시점에서 추론한다.

* `as?` 연산자를 활용하면 값을 다른 타입으로 변환하는 것과 변환이 불가능한 경우를 처리하는 것을 한번에 할 수 있다.

* 자바에서 가져온 타입은 플랫폼 타입으로 취급된다.

* 널이될 수 있는 원시타입은 자바에서 참조타입으로 변환된다.

* `Any`타입은 모든 타입의 조상이며 자바의 `Object`에 해당된다. 

* 정상적으로 끝나지 않을 함수를 선언할 때 `Nothing`타입을 사용한다.

* 코틀린의 컬렉션은 자바의 표준 컬렉션 클래스를 사용한다. 더 개선하여 이를 읽기 전용 콜렉션과 변경 가능 컬렉션으로 구별해 제공함

* 자바 클래스를 확장하여 사용할 때 파라미터의 널 가능성과 변경 가능성에 대해 생각해야 한다.

* 성능이 중요한 코드이면 원시타입의 배열을 활용하자.


## 프로퍼티 접근자 로직 재활용: 위임 프로퍼티

위임 프로퍼티를 활용하면 값을 백킹 필드에 저장하는 것보다 더 복잡한 방식으로 작동하는 프로퍼티를 구현할 수 있다. 이를 위해서는 `위임`을 해야하며 이 작업을 하는 객체를 `위임 객체`라고 한다. 

### 위임 프로퍼티 소개

일반적인 문법은 다음과 같다.

```
class Foo {
	var p: Type by Delegate()
}
```

위임 프로퍼티는 접근자 로직을 다른 객체에게 위임한다. `by`뒤에 있는 `Delegate`클래스를 활용하여 위임에 쓰일 객체를 얻는다.

```
class FOO {
	private val delegate = Delegate() // 컴파일러가 생성한 도우미 프로퍼티다.
    var p: Type
    set(value:Type) = delegate.setValue(..., value)
    get() = delegate.getValue(...)
}
```

프로퍼티 위임 관례에 따르는 `Delegate`클래슨느 `getValue`와 `setValue` 메소드를 제공해야 한다. 
```
class Delegate {
	operator fun getValue() { ... }
    operator fun setValue() { ... }
}

class Foo {
	var p: Type by Delegate() // by 키워드는 프로퍼티와 위임 프로퍼티를 연결한다.
}

val foo = Foo()
val oldValue = foo.p // delegate.getValue()
foo.p = newValue // delegate.setValue()
```


### 위임 프로퍼티 사용: by lazy()

지연 초기화 `lateinit var`은 객체의 일부분을 초기화하지 않고 남겨뒀다가 실제로 그 부분의 값이 필요할 경우 초기화할 때 쓰이는 패턴이다. 초기화 과정에서 자원이 많이 사용되거나 사용할 때 마다 초기화하지 않아도 되는 프로퍼티에 대해 사용한다.

다음은 지연 초기화를 백킹필드를 활용해 비교해보자.
```
// by lazy
private lateinit var email by lazy {
	loadEmails()
}

// backing field
private var _emails: List<Email>? = null
val emails: List<Email>
	get() {
    	if (_emails == null) {
        	_emails = loadEmails(this)
        }
        return _emails
    }

```

이런 형식의 코드는 안드로이드의 바인딩에서도 활용된다.

```
private var _binding: ActivityBinding? = null
private val binding: ActivityBinding get() = _binding
	
override fun onCreate() {
	_binding = ActivityBinding.inflate( ... )
}
```

하지만 이런 코드를 만드는 일은 성가시다. 게다가 이 구현은 스레드에 안전하지 않아 제대로 작동한다고 말할 수 없다. 코틀린은 더 나은 해결법을 위해 `위임 프로퍼티`를 제공한다. `lazy`를 활용하면 해당 프로퍼티에 단 한번만 값이 초기화하는 것을 보증한다.

```
class Person(val nmae: String) {
	val emails by lazy { loadEmails(this) }
}
```

### 위임 프로퍼티의 구현

[lateinit / lazy로 지연시키기](https://velog.io/@cksgodl/Kotlin-lateinit-lazy-%EB%A1%9C-%EC%A7%80%EC%97%B0%EC%8B%9C%ED%82%A4%EA%B8%B0#late-initialized-properties-and-variables)에서 한번 본것 처럼 어떻게 구현되어있는지 확인해보자.

자바에서는 `PropertyChangeSupport`와 `PropertyChangeEvent` 클래스를 활용해 어떠한 프로퍼티가 바뀔때 마다 리스너에게 변경 통지를 보낼 수 있다.

```
class ObservableProperty(
	val propName: String,
    var propValue: Int,
    val changeSupport: PropertyChangeSupport
) {
	fun getValue(): Int = propValue
    fun setValue(newValue: Int) {
    	val oldValue = propValue
        propValue = newValue
        chagneSupport.firePropertyChange(propName, oldValue, newValue)
    }
}

class Person(
	val name: String, age: Int, salary: Int
) : PropertyChangeAware() {
	
    val _age = ObservableProperty("age", age, changeSupport)
    var age: Int
    	get() = _age.getValue()
        set(value) { _age.setValue(value) }
}


val p = Person("Dmitry", 34, 2000)
p.addPropertyChangeListenr(
	PropertyChangeListener { event ->
    	println("Property ${event.propertyName} changed from ${event.oldValue} to ${event.newValue}"
    }
)

p.age = 35 // Property age changed form 34 to 35
```

해당 방식은 코틀린의 위임 프로퍼티와 비슷하다. 코틀린의 `Delegate`프로퍼티와 비슷하게 변경 통지를 전달하는 클래스를 만들어 사용한다. 하지만 게터와 세터에서 상당한 준비 코드가 필요하다. 코틀린의 위임 프로퍼티 기능을 활용하면 이런 코드를 없앨 수 있다.

`by` 위임을 사용하기 위해서는 메소드 시그니처를 코틀린의 관례에 맞게 살짝 수정해야 한다.

```
class ObservableProperty(
    var propValue: Int,
    val changeSupport: PropertyChangeSupport
) {
	operator fun getValue(p:Person, prop: KProperty<*>): Int = propValue
    operator fun setValue(p:Person, prop: KProperty<*>, newValue: Int) {
    	val oldValue = propValue
        propValue = newValue
        chagneSupport.firePropertyChange(propName, oldValue, newValue)
    }
}

```

* `KProperty.name`을 통해 메소드가 처리할 프로퍼티 이름을 알 수 있다.
* `getValue`, `setValue` 메소드는 `operator`한정자가 붙는다.

이러한 코드를 위임패턴을 사용해 구현해보자.
```
class Person(
	val name: Stirng, age: Int, salary: Int
) : PropertyChnageAware() {
	val age: Int by ObservableProperty(age, changeSupport)
    val salary: Int by ObservableProperty(salary, changeSupport)
}
```

`by`키워드를 활용해 위임 객체를 지정하면 상속을 받지 않아도 메소드들을 자동으로 위임해준다. 코틀린은 위임 객체를 감춰진 프로퍼티에 저장하고, 주 객체의 프로퍼티를 읽거나 쓸 때마다 위임 객체의 `getValue`, `setValue`를 호출한다.

## 정리

* 코틀린에서는 정해진 이름의 함수를 오버로딩함으로써 표준 수학 연산자를 오버로딩할 수 있다.

* 비교 연산자는 `equals`와 `compareTo`로 변환된다.

* 관례에 따라 `rangeTo`, `iterator`함수를 정의하여 범위를 만들거나 컬렉션과 배열의 원소를 이터레이션할 수 있다.

* `JS`와 같이 구조분해를 사용할 수 있다.

* 위임 프로퍼티를 통해 프로퍼티 값을 저장하거나 초기화하거나 읽거나 변경할 때 사용하는 로직을 재활용할 수 있다. 위임 프로퍼티는 프레임워크를 만들 때 유용하다.

* `lazy`프로퍼티를 통해 지연 초기화 프로퍼티를 쉽게 구현할 수 있다.

* `Delegates.observable`함수를 사용하면 프로퍼티 변경을 관찰할 수 있는 관찰자를 쉽게 추가할 수 있다.

* 맵을 위임 객체로 사용하는 위임 프로퍼티를 통해 다양한 속성을 제공하는 객체를 유연하게 다룰 수 있다.
```
private val _attributes = hashMapOf<String, String>()
fun setAttribute(attrName: String, value: String) {
	_attributes[attrName] = value
}

val name: String
	get() = _attributes["name"]!!
    
val name: String by _attributes // 위임 프로퍼티 활용
```



# 고차 함수: 파라미터와 반환 값으로의 람다 활용

> 함수 타입 : 함수의 타입을 가진 변수로써 함수 참조를 함수의 인자로 넘길 수 있다.

```
val sum: (Int, Int) -> Int = { x, y -> x + y }
val action: () -> Unit = { println(42) }
```

함수 타입에서 파라미터 이름을 지정하면 `IDE`가 해당 람다를 활용할 때 도움을 준다.
```
val callBack: (code: Int, content: String) -> Unit
```

### 람다를 자바로 디컴파일

코틀린의 함수 타입의 변수는 자바의 `FunctionN`인터페이스를 구현하는 객체로 저장된다. 코틀린 표준 라이브러리는 함수 인자의 개수에 따라 `Function0<R>`, `Function1<P1, R>`등의 인터페이스를 제공한다. 이들은 `invoke`를 호출하여 함수를 실행한다. (무명 클래스로 컴파일 되어 넘어감)


### 함수를 함수에서 반환

함수가 함수를 반환하는 경우가 있다. 다음 예를 보자.

```
fun getShippingCostCalculator(
	delivery: Delivery
) : (Order) -> Double {
	if (delivery == Delivery.DEXPEDITED) {
    	return { order -> 6 + 2.1 * order.itemCount }
    } else {
    	order -> 1.2 * order.itemCount
    }
}

val calculator = getShippingCostCalculator(Delivery.EXPEDITED)

calculator(Order(3)) // 12.3
```

위의 예는 배달의 종류에 따라 배달비를 따로 계산하는 함수를 반환하는 함수이다. 
또한 술어를 반환하는 함수를 정의할 수 있다.


### 람다를 활용한 중복 제거

람다 식은 재활용하기 좋은 코드를 만들 때 쓸 수 있는 훌륭한 도구이다. 람다를 사용할 수 없는 환경에서 아주 복잡한 구조를 만들어야만 하는 코드를 람다를 활용하면 쉽게 제거할 수 있다.

```
val log = listOf(
	SiteVisite("/", 34.0, OS.WINDOWS),
	SiteVisite("/", 22.0, OS.MAC),
	SiteVisite("/login", 12.0, OS.WINDOWS),
	SiteVisite("/signup", 8.0, OS.IOS),
	SiteVisite("/", 16.3, OS.ANDROID),
)
```

해당 로그에서 윈도우 사용자의 평균 방문시간을 구해보자. `average`함수를 사용하면 쉽게 그런 작업을 수행할 수 있다.

```
val averageWindowsDuration = log
	.filter { it.os == OS.WINDOWS }
    .map(SiteVisite::duration)
    .average()
```

이를 확장함수로 추출하여 맥에 대한 평균 방문시간을 다시 계산해보자.

```
fun List<SiteVisite>.averageDurationFor(os: Os) 
	= filter { it.os == os }.map(SiteVisite::duration).average()

log.averageDurationFor(OS.MAC)
```

이런 함수는 편리하다. 하지만 충분히 강력하지 않다. 모바일 디바이스사용자 (`Android`, `IOS`)의 평균 방문시간을 구하고 싶다면 어떻게 해야할까?

```
log.filter { it.os in setOf(OS.IOS, OS.ANDRIOD) }
	.map(SiteVisite::duration)
    .average()
```

어찌저지 적을 순 있다. 하지만 `IOS`사용자의 `/signup`페이지의 평균 방문시간을 구하라? 라고 하면 새로운 함수를 계속해서 만들어야 할 것이다. 이러한 상황에서는 람다가 유용하다. 함수 타입을 사용하면 필요한 조건을 파라미터로 뽑아낼 수 있다.

```
fun List<SiteVisit>.averageDurationFor(predicate: (SiteVisit) -> Boolean) 
	= filter(predicate).map(SiteVisite::duration).average()
    
log.averageDurationFor ({ it.is in setOf(OS.ANDROID, OS.IOS) })
log.averageDurationFor ({ it.os == OS.IOS && it.paht == "/signup" })
```

코드 중복을 줄일 때 함수 타입이 상당히 도움이 된다. 하지만 5개 이상의 너무 많은 람다를 인자로 넘기지는 말자 가독성이 떨어진다.


## 인라인 함수: 람다의 부가 비용 없애기

람다 식을 자바로 디컴파일 할 떄마다 `FunctionN`이라는 무명 클래스가 만들어지고 실행할 땐 이의 `invoke`가 수행되며 람다함수가 실행된다. 무명 클래스의 생성에는 부가 비용이 든다. 따라 람다를 사용하는 구현은 똑같은 작업을 수행하는 일반 함수를 사용한 구현보다 덜 효율적이다.

> 그렇다면 반복되는 코드를 별도의 `API`로 빼내되 컴파일러가 자바의 일반 명령문만큼 효율적으로 코드를 생성하게 할 수는 없을까? 코틀린 컴파일러에서는 `inline`한정자를 붙이여 이를 해결할 수 있다.

### 인라인함수의 작동

어떤 함수를 `inline`하면 함수의 본문이 인라인 된다. 즉 함수의 내용이 본문으로 들어온다.

```
inline fun printHello(times: Int) {
	repeat(times) {
    	println("Hello!")
    }
}

fun main() {
	printHello(5)
    
    // 동일
	repeat(5) { 
    	println("Hello!")
    }
}
```

람다를 활용하는 모든 함수를 인라이닝할 수는 없다. 함수가 인라이닝될 때 그 함수에 인자로 전달된 람다 식의 본문은 결과 코드에 직접 들어갈 수 있다. 하지만 이렇게 람다가 본문에 직접 펼쳐지기 떄문에 함수가 파라미터로 전달받은 람다를 본문에 사용하는 방식이 한정될 수 밖에 없다. 

> 함수본문에서 파라미터로 받은 람다를 호출한다면 그 호출을 쉽게 람다 본문으로 바꿀 수 있다. 하지만 파라미터로 받은 람다를 다른 변수에 저장하고 나중에 그 변수를 사용한다면 람다를 표현하는 객체가 어딘가는 존재해야 하기 때문에 람다를 인라이닝할 수 없다.

`noinline`한정자를 사용하여 인라인 함수에서의 람다함수를 인라이닝을 금지할 수 있다.

### 자원관리를 위한 인라인함수 `use`

`use`는 닫을 수 있는(closable)한 자원에 대한 확장 함수이며 람다를 인자로 받는다. 이는 람다를 호출 한 후에 자원을 닫아준다. 정상 종료는 물론 람다 안에서 예외가 발생한 경우에도 자원을 확실하게 닫는다. 물론 `use`도 인라인 함수이며 사용해도 성능에는 영향이 없다.

```
BufferedReader(FileReader(path)).use { br ->
	return br.readLine()
}
```

해당 람다의 본문 안에서 사용한 `return`은 `non-local`한 리턴이다. 람다를 끝내는 것이 아니라 `readFirstLineFormFile`함수를 끝내면서 값을 반환한다.

## 고차 함수 안에서 흐름 제어

자신을 둘러싸고 있는 블록보다 더 바깥에 있는 다른 블록을 반환하게 만드는 `return`문을 `넌 로컬 리턴`이라고 부른다. 이러한 바깥쪽 함수를 반환시킬 수 있는 때는 람다를 인자로 받는 함수가 인라인 함수인 경우일 뿐이다.

```
(0..20).forEach {
	if(it%2 == 0) return@forEach
    if(it == 10) return
    print(it)
} // 1,3,5,7,9
```

해당 예처럼 레이블을 붙여 로컬에 대한 `return`도 활용할 수 있다. 리턴 앞에 해당 식을 추가하면 된다.

```
people.forEach lable@{
	if(it.name=="Alice") return@label
}
```

무명 함수를 활용하여 넌 로컬 리턴을 구현할 수도 있다.

```
fun lookForAlice(people: List<Person>) {

	people.forEach(fun(person) { // 여기로 리턴 됨
		if(person.name == "Alice") return
	})
}
```


## 정리

* 함수 타입을 사용해 함수에 대한 참조를 담는 변수나 파라미터나 반환 값을 만들 수 있다.

* 고차 함수는 다른 함수를 인자로 받거나 반환한다. 함수의 파라미터 타입이나 반환 타입으로 함수 타입을 사용하면 고차 함수를 선언할 수 있다.

* 인라인 함수를 컴파일 하면 함수의 본문에 람다의 본문을 추가해 준다. 무명 클래스가 생기지 않음으로 비용이 들지 않는다.

* 인라인 함수에서는 람다 안에 있는 `return`문이 바깥족 함수를 반환시키는 `non-local return`을 사용할 수 있다.

* 무명 함수는 람다 식을 대신할 수 있으며 `return`식을 처리하는 규칙이 일반 람다 식과는 다르다. 람다 본문 여러곳에서 `return`을 해야한다면 무명 함수를 쓸 수 있다.


# 제네릭스


### 제네릭 타입 파라미터

제네릭스를 사용하면 `타입 파라미터`를 받는 타입을 정의할 수 있다. 예를 들어 `List`라는 타입이 있다면 그 안에 들어가는 원소의 타입을 안다면 쓸모가 있을 것이다. 타입 파라미터를 사용하면 **이 변수는 리스트다**라고 말하는 대신 정확하게 **이 변수는 문자열을 담는 리스트다**라고 말할 수 있다. 

```
val readers = mutableListOf<String>()

val readers: MutableList<String> = mutableListOf()
```

#### 제네릭 함수와 프로퍼티

리스트를 다루는 함수를 정의할 때 특정 타입의 리스트를 다루는 것 뿐만 아니라 모든 타입의 리스트를 다룰 수 있는 함수를 원할 수도 있다. 이럴 때 제네릭 함수를 사용한다.

```
fun <T> List<T>.slice(indices: IntRange): List<T>
// 제네릭 함수인 slice는 T를 타입 파라미터로 받는다.
```


수신 객체와 반환 타입 모두 `List<T>`이다. 이런 함수를 구체적인 리스트에 대해 호출할 때 타입 인자를 명시적으로 지정할 수 있다. 하지만 실제로는 대부분 컴파일러가 알아서 추론해준다.

다음 예로 `filter`가 돌아가는 방식을 보자.

```
fun <T> List<T>.filter(predicate: (T) -> Boolean): List<T>

val readers = mutableListOf("이해찬", "장준용")
readers.filter { it.first() != '이' } // 장준용
```

변수 `it`의 타입은 `T`라는 제네릭 타입이다. 수신 객체의 타입을 보고 추론하여 `String`으로 변환해 준다. 

또한 제네릭 확장 프로퍼티도 선언할 수 있다.
```
val <T> List<T>.penultimate: T
	get() = this[size-2]
    
(1..4).penultimate() // 2
```

일반 프로퍼티는 제네릭이 될 수 없다.
```
val <T> x: X = TODO() // ERROR!! type parameter of a property must be sued in its receiver type
```


#### 제네릭 클래스의 선언

클래스, 인터페이스도 제네릭하게 만들 수 있다. 

```
interface List<T> {
	operator fun get (index:Int): T
	// ...
}
```

해당 클래스나 인터페이스를 상속받는 클래스는 제네릭 파라미터에 대해 타입 인자를 지정해야 한다. 이때 구체적인 타입을 넘길 수도 있고 타입 파라미터로 바든 타입을 넘길 수 도 있다.

```
class StringList: List<String> {
	override fun get(index: Int): String = ...
}

calss ArrayList<T>: List<T> {
	override fun get(index: Int): T = ...
}
```

`StringList`클래스는 `String`타입 원소만을 포함한다. 하지만 `ArrayList`클래스는 자신만의 타입 파라미터를 정의하면서 T를 기반으로 클래스를 정의한다. 


### 타입 파라미터 제약

> 타입 파라미터 제약은 클래스나 함수에 사용할 수 있는 타입 인자를 제한하는 기능이다.

예를 들어 리스트의 모든 원소의 합을 구하는 `sum`함수를 구현할 때, `List<Int>`, `List<Double>`은 가능하지만 `List<String>`은 안 되기 때문이다. 이 떄는 타입 파라미터로 숫자 타입만 허용하게 할 수 있다.

```
fun <T : Number> List<T>.sum() : T
```

타입파라미터의 콜론 뒤에 상한 타입을 지정할 수 있다. `T`에 대한 상한을 정하고 나면 `T`타입의 값을 그 상한 타입의 값으로 취급할 수 있다.   

#### 널이 될 수 없는 타입 파라미터

제네릭 클래스나 함수를 정의하고 그 타입을 인스턴스화할 때는 널이 될 수 있는 타입을 포함하는 어떤 타입으로 타입 인자를 지정해도 타입 파라미터를 치환할 수 있다. 아무런 상한을 정하지 않은 타입 파라미터는 결과적으로 `Any?`를 상한으로 정한 파라미터와 같다.

```
class Processor<T> {
	fun process(value: T) {
    	value?.hashCode() // value가 NUll이 될 수 있기에 안전호출
    } 
}
```

널가능성을 배제하고자 하면 `Any?` 대신에 `Any`를 사용해야 한다.

```
class Processor<T : Any> {
	fun process(value: T) {
    	value.hashCode() 
    } 
}
```

## 실행 시 제네릭스의 동작


코틀린의 제네릭 타입 인자 정보는 런타임에 지워진다. 

> 제네릭 클래스 인스턴스가 그 인스턴스를 생성할 때 쓰인 타입 인자에 대한 정보를 유지하지 않는다는 뜻

`List<String>` 객체를 만들고 안에 문자열을 여럿 넣더라고 실행 시점에는 그 객체를 오직 `List`로만 볼 수 있다. 어떤 타입의 정보를 저장하는지는 알 수 없음

```
val list1: List<String> = listOf("a", "b")
val lsit2: List<Int> = listOf(1, 2)
```
 
코드를 실행할 때 두 객체는 그저 `List`로 판단된다.

> 이렇게 제네릭 타입을 저장하지 않는 것을 **타입 소거**라고 한다.

따라서 실행시점에 타입 인자를 검사할 수 없다. 예를 들어 어떤 리스트가 문자열로 이뤄진 리스트인지 다른 객체로 이뤄진 리스트인지 실행 시점에 검사할 수 없다.
```
if (value is LIst<String>) // ...
// ERROR! : Cannot check for instacne of erased type
```
 
코틀린에서는 타입 인자를 명시하지 않고 제네릭 타입을 사용할 수 없다. 그렇다면 어떤 값이 집합이나 맵이 아니라 리스트라는 사실은 어떻게 확인할까? 바로 **스타 프로젝션**을 사용하면 된다.

```
if (value is List<*>) { /*..*/ }
```
 
이도 `value`가 `List`임은 알 수 있지만 그 우너소 타입은 알 수 없다. 


#### as? as에 제네릭 타입 사용하기

실행 시점에는 제네릭 타입의 타입 인자를 알 수없으므로 캐스팅은 항상 성공한다. 하지만 그런 캐스팅을 사용하면 컴파일러가 `unchecked cast`경고를 해준다.

```
fun printSUm(c: Collection<*>) {
	val intList = c as? List<Int>
    	?: throw IllegalArgumentException("List is expected")
	println(intList.sum())
}
```
컴파일러가 캐스팅 관련 경고를 한다는 점 제외하면 모든 코드가 문제없이 컴파일된다.

```
printSum(listOf("a", "b", "c")) // 캐스팅은 성공 But sum()함수에서 오류
```

코틀린 컴파일러는 컴파일 시점에 타입 정보가 주어진 경우에는 is 검사를 수행하게 해준다.
```
fun printSUm(c: Collection<Int>) {
  	if (c is List<Int>) {
  		println(c.sum())
  	}
}
```

코틀린은 제네릭 함수 본문에서 함수의 타입 인자를 가리킬 수 있는 특별한 기능을 제공하지 않는다. 하지만 `inline`함수 안에서는 타입 인자를 사용할 수 있다. 이제 그 기능에 살펴보자.

### 실체화(reified)한 타입 파라미터를 사용한 함수 선언

함수를 `inline`으로 선언하면 무명 클래스와 객체가 생성되지 않아서 성능이 더 좋아질 수 있다. 더해 타입 파라미터를 `reified`로 지정하면 `value`의 타입이 `T`의 인스턴스인지를 실행 시점에 검사할 수 있다.

```
inline fun <reified T> isA(value: Any) value is T 

isA<String>("ABC") // true
```

코틀린 콜렉션 `API`에서 `filetrIsInstacne`도 `reified`를 사용하고 있다.

```
inline fun <reified T> Iterable<*>.filterIsInstance() : List<T> { 
	//...
}
```
 
 > 자바 코드에서는 `reified` 타입 파라미터를 사용하는 `inline`함수를 호출할 수 없다. 
 

`reified`한정자를 이용해 안드로이드에서의 `startActivity`함수를 더 간단하게 만들 수 있다.
```
inline fun <reified T: Activity> Context.startActivity() {
	val intent = Intent(this, T::class.java)
    startActivity(intent)
}

startActivity<DetailActivity>()
```

## 제네릭과 하위 타입

`List<Any>` 타입의 파라미터를 받는 함수에 `List<String>`을 넘기면 안전할까? `Any`는 `String`의 상위 타입으로 이는 안전하다. 하지만 `Any`와 `String`이 `List`인터페이스의 타입 인자로 들어가는 경우 안전성을 보증할 수는 없다. 

```
fun addAnswer(list: MutableList<Any>) {
	list.add(42)
}

val strings = mutableListOf("abc","efg")
addAnswer(strings)
strings.maxBy { it.length } // ERROR! 
```

코틀린 컴파일러는 실제 이런 함수 호출을 금지한다. 어떤 함수가 리슽의 원소를 추가하거나 변경한다면 타입의 불일치가 생길 수 있어서 `List<String>`을 넘길 수 없다. 하지만 원소 추가나 변경이 없는 경우 `List<String>`을 `List<Any>`대신 넘겨도 안전하다.

함수가 읽기 전용 리스트를 받는다면 리스트를 그 함수에 넘길 수 있을 것이다.

### 클래스, 타입, 하위 타입

어떤 타입 A의 값이 필요한 모든 장소에 어떤 타입 B의 값을 넣어도 아무 문제가 없다면 타입 B는 타입 A의 하위 타입이다. 예를 들어 `Int`는 `Number`의 하위 타입이지만 `String`의 하위타입은 아니다. 이 정의는 모든 타입이 자신의 하위 타입이라는 뜻이기도 하다.

이러한 타입검사는 변수 대입이나 함수 인자 전달 시 하위 타입 검사를 매번 수행한다.

```
fun test(i: Int) {
	val n: Number = i // 컴파일 가능
    
    fun f(s: String) { /* ... */ }
    f(i) // 컴파일 에러
}
```

하위 타입과 하위 클래스는 살짝 다르다. `Int`클래스는 `Number`의 하위 클래스이므로 `Int`는 `Number`의 하위 타입이다. 하지만 `Int`는 `Int?`의 하위 타입이지만 `Int?`는 `Int`의 하위 타입이 아니다.

널이 될 수 없는 타입은 널이 될 수 있는 타입의 하위 타입이다. 하지만 두 타입 모두 같은 클래스이다.

```
val s: String = "abc"
val t: String? = s // 가능 하위타입임
```

이러한 하위 타입과 하위 클래스의 차이는 제네릭을 이야기할 떄 중요해 진다. "`List<String>` 타입의 값을 `List<Any>`를 파라미터로 받는 함수에 전달해도 괜찮은가?"라는 질문을 하위 타입 관계를 써서 다시 쓰면 "`List<String>`은 `List<Any>`의 하위 타입인가?" 이다. 
위의 예에도 보았듯이 `List<String>`은 `List<Any>`의 하위 타입이 아니다.

인스턴스 타입 사이의 하위 타입 관계가 성립하지 않으면 그 제네릭 타입을 `무공변`이라고 한다. `MutableList`를 예로 들면 `A`와 `B`가 서로 다르기만 하면 `MutableList<A>`는 항상 `MutableList<B>`의 하위 타입이 아니다. 자바에서는 모든 클래스가 무공변이다.  

코틀린의 `List` 인터페이스는 읽기 전용 컬렉션을 표현한다. `A`가 `B`의 하위 타입이면 `List<A>`는 `List<B>`의 하위 타입이다. 그런 클래스나 인터페이스를 `공변적`이라 말한다. 


### 공변성 : 하위 타입 관계를 유지

고양이는 동물의 하위 타입이기에 `List<Cat>`은 `List<Animal>`의 하위 타입이다. 

코틀린의 제네릭 클래스가 타입 파라미터에 대해 공변적임을 표시하려면 타입 파라미터 이름 앞에 `out`을 붙여 표현한다.

```
interface Producer<out T> { // T에 대해 공변적이라고 선언
	fun produce() : T
}
```

> 클래스의 타입 파라미터를 공변적으로 만들면 함수 정의에 사용한 파라미터 타입과 타입 인자의 타입이 일치하지 않더라고 그 클래스의 인스턴스를 함수 인자나 반환값으로 사용할 수 있다.

```
class Herd<T : Animal> {
	val size: Int get() = ...
    operator fun get(i: Int): T { /* ... */ } 
}

fun feddAll(animals: Herd<Animal>) {
	for(i in 0 until animals.size) {
    	animals[i].feed()
    }
}

class Cat : Animal() {
	fun cleanLitter() { /* ... */ }
}

fun takeCareCats(cats: Herd<Cat>) {
	feedAll(cats) // ERROR! inferred type is Herd<Cat>, But Herd<Aniimal> was Expected
}
```

`Herd`클래스의 `T` 타입 파라미터에 아무런 변성도 지정하지 않았기 때문에 고양이 무리는 동물 무리의 하위 클래스가 아니다.  `Herd`클래스 의 타입파라미터를 공변적으로 바꾸면 이는 사용이 가능하다.

```
class Herd<out T : Animal> {
	// ...
}
```

> T가 함수의 반환 타입에 쓰인다면 T는 `out`위치에 있다. 그 함수는 T 타입의 값을 "생산"한다. T가 함수의 파라미터 타입에 쓰인다면 T는 인 위치에 있다. 그런 함수는 T 타입의 값을 "소비"한다.

```
interface Transformer<T> {
	fun transform(t: T("인" 위치)): T ("아웃" 위치)
}
```

`T`앞에 `out`키워드를 붙이면 클래스 안에서 메소드가 아웃 위치에서만 `T`를 사용하게 하고, 인 위치에서는 `T`를 사용하지 못하게 막는다.

* 공변성 : 하위 타입의 관계가 유지된다.
* 사용 제한 : `T`를 아웃 위치에서만 사용할 수 있다.

`List<T>`는 읽기 전용이며 이는 값을 반환하기만 한다.

```
interface List<out T> : Collectino<T> {
	operator fun get(index: Int): T

	fun subList(fromIndex: Int, toIndex: Int): List<T>
	
	//..
}
```

`MutableList<T>`는 공변적이지 않고 인과 아웃 위치에 동시에 쓰인다.

```
interface MutableList<T>: List<T>, MutableCollection<T> {
	override fun add(element: T): Boolean
}
```

### 반공변성 : 뒤집힌 하위 타입 관계

`반공변성`은 공변성을 거울에 비친 상이라 할 수 있다. 반공변 클래스의 하위 타입 관계는 공변 클래스의 경우와 반대이다. 

> 타입 B가 타입 A의 하위 타입인 경우 `Consumer<A>`가 `Consumer<B>`의 하위 타입인 관계가 성립되면 제네릭 클래스 `Consumer<T>`는 타입 인자 `T`에 대해 반공변이다. 

A와 B의 순서가 바뀐 것을 유의하자. `Consumer<Animal>`이 `Consumer<Cat>`의 하위 타입이다. 

```
Animal <- Cat // 하위 타입
Producer<Animal> <- Producer<Cat> // 공변성
Consumer<Animal> -> Consumer<Cat> // 반공변성
```

#### 공변성
1. 타입 인자의 하위 타입 관계가 제네릭 타입에서도 유지된다.
2. `Producer<Cat>`은 `Producer<Animal>`의 하위 타입이다.
3. `T`를 아웃위치에서만 사용할 수 있다.

#### 반공변성
1. 타입 인자의 하위 타입관계가 제네릭 타입에서 뒤집힌다.
2. `Consumer<Animal>`은 `Consumer<Cat>`의 하위 타입이다.
3. `T`를 인위치에서만 사용할 수 있다.

### 사용 지점 변성 : 타입이 언급되는 지점에서 변성 지정 가능

```
fun <T> copyData(source: MutableList<out T>, destination: MutableList<T>) {
	for(item in source) {
    	destination.add(item)
    }
}
```

함수 파라미터에 변성 변경자를 추가하여 사용지점에 따라 변성을 추가할 수 있다.

타입 선언에서 타입 파라미터를 사용하는 위치라면 어디에나 변성 변경자를 붙일 수 있다. 따라서 파라미터 타입, 로컬 변수 타입, 함수 반환 타입 등 타입파라미터가 쓰이는 경우 `in`이나 `out`변경자를 붙일 수 있다. 이때 `타입 프로젝션(Type Projection)`이 일어난다. 

> 즉 `source`를 일반적인 `MutableList`가 아니라 `MutableList`를 프로젝션을 한 타입으로 만드는 것이다.

이 경우 `copyData` 함수는 `MutableList`의 메소드 중에서 반환 타입으로 타입 파라미터 `T`를 사용하는 메소드만 호출할 수 있다. 

### 스타 프로젝션: 타입 인자 대신 * 사용하기

제네릭 타입 인자 정보가 없음을 표현하기 위해 `스타 프로젝션(*)`을 사용한다고 말했다. 예를 들어 원소 타입이 알려지지 않은 리스트는 `List<*>`라는 구문으로 표현할 수 있다. 이 스타프로젝션의 의미는 무엇일까?

 `MutableList<*>`는 `MutableList<Any?>`와 같지 않다. `MutableList<Any?>`는 모든 타입의 원소를 담을 수 있다는 사실을 알 수 있는 리스트이다. 하지만 `MutableList<*>`은 어떤 정해진 구체적인 타입의 원소만을 담는 리스트지만 그 원소의 타입을 정확히 모른다는 사실을 표현한다.  그 뜻은 리스트가 `String`과 같은 구체적인 타입의 원소를 저장하기 위해 만들어진 것이라는 뜻이다. 아무 원소나 막 다 담아도 된다는 뜻이 아니다. 

컴파일러는 `MutableList<*>`를 `MutableList<out Any?>`처럼 동작한다. `Any?`타입의 원소를 꺼내올 수는 있지만 타입을 모르는 리스트에 원소를 마음대로 넣을 수는 없다.

스타 프로젝션을 사용할 때는 값을 만들어내는 메소드만 호출할 수 있고 그 값의 타입에는 신경을 쓰지 말아야 한다. 

## 정리

* 제네릭 타입의 타입 인자는 컴파일 시점에만 존재한다.

* 타입 인자가 실행 시점에 지워지므로 타입 인자가 있는 타입을 `is`연산자를 통해 검사할 수 없다.

* 인라인 함수의 매개변수를 `reified`로 표시하여 실체화하면 타입을 검사할 수 있다.

* 제네릭 클래스의 타입 파라미터가 아웃 위치에서만 사용되는 경우(생산자) 그 타입 파라미터를 `out`으로 표시해서 공변적으로 바꿀 수 있다.

* 공변적인 경우와 반대로 제네릭 클래스의 타입 파라미터가 인 위치에서만 사용되는 경우(소비자) `in`으로 표시해 반공변적으로 만들 수 있다.

* 읽기 전용 콜렉션 `List`인터페이스는 공변적이다. 따라서 `List<String>`은 `List<Any>`의 하위 타입이다.

* 선언 지점 변성 - 제네릭 클래스의 공변성을 전체적으로 지정

* 사용 지점 변셩 - 구체적인 사용위치에서 변성을 적용

* 제네릭 클래스의 타입 인자가 어떤 타입인지 정보가 없거나 타입 인자가 어떤 타입인지가 중요하지 않을 때 스타 프로젝션 구문을 사용할 수 있다.

# DSL 만들기

### [[Kotlin] DSL를 활용하여 나만의 Custom Test 메소드 만들어보자](https://velog.io/@cksgodl/Kotlin-DSL%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%98%EC%97%AC-%EB%82%98%EB%A7%8C%EC%9D%98-Custom-Test-%EB%A9%94%EC%86%8C%EB%93%9C-%EB%A7%8C%EB%93%A4%EC%96%B4%EB%B3%B4%EA%B8%B0)

### [[Kotlin] 복잡한 객체를 생성하기 위한 DSL을 정의하라](https://velog.io/@cksgodl/Kotlin-%EB%B3%B5%EC%9E%A1%ED%95%9C-%EA%B0%9D%EC%B2%B4%EB%A5%BC-%EC%83%9D%EC%84%B1%ED%95%98%EA%B8%B0-%EC%9C%84%ED%95%9C-DSL%EC%9D%84-%EC%A0%95%EC%9D%98%ED%95%98%EB%9D%BC)

### [[Android/Kotlin] 버튼을 생성하는 DSL을 만들어 Compose같이 버튼을 만들어보자](https://velog.io/@cksgodl/AndroidKotlin-%EB%B2%84%ED%8A%BC%EC%9D%84-%EC%83%9D%EC%84%B1%ED%95%98%EB%8A%94-DSL%EC%9D%84-%EB%A7%8C%EB%93%A4%EC%96%B4-Compose%EA%B0%99%EC%9D%B4-%EB%B2%84%ED%8A%BC%EC%9D%84-%EB%A7%8C%EB%93%A4%EC%96%B4%EB%B3%B4%EC%9E%90)

다음 링크 참조


# 코틀린 1.1, 1.2, 1.3에서 업데이트 된 점


## 코틀린 1.1

### 타입 별명 `typealias`

주로 사용하는 타입에 다른 이름을 붙이거나, 짧은 이름을 붙일 수 있다.

```
// 콜백 함수 별명
typealias MyHandler = (Int, String, Any) -> Unit

fun addHandler(h:MyHnadler) { ... }

// 컬렉션에 대한 별명
typealias Args = Array<String>

// 제네릭 타입 별명
typealis StringKeyMap<V> = Map<String, V>
val myMap: StringKeyMap<Int> = mapOf("One" to 1)

// 중첩클래스에 대한 별명
class Foo {
	class Bar {
    	inner class Baz
    }
}
typealis FooBarBaz = Foo.Bar.Baz
```
최상위 수준에서만 타입 별명을 정의할 수있다.


### 람다 파라미터의 구조 분해
```
val nums = listOf(1, 2, 3)
val names = listOf("One", "Two", "Three")
(nums zip names).forEach { (num, name) -> println("$num = $name")}
```

### 프로퍼티 접근자에 대한 인라이닝

프로퍼티 접근자도 함수이므로 코틀린 `1.1`부터는 접근자를 `inline`으로 설정할 수 있다. 게터 뿐만 아니라 세터도 인라이닝이 가능하며, 확장 멤버 프로퍼티나 최상위 프로퍼티도 인라이닝이 가능하다.

프로퍼티에 뒷받침하는 필드가 있으면 프로퍼티의 게터나 세터를 인라이닝할 수 없다.

```
val topLevel: Double
	inline get() = Math.PI
    
class InlinePropExample(var value: Int) {
	var setOnly: Int
    	get() = value
        inline set(v) { value = v }
    // inline property cannot have backing field    
    val backing: Int = 10
    	inline get() = field * 1000
}
```

### `reified`활용해 제네릭 타입으로 이넘 값 접근

```
enum calss DAYSOFWEEK { MON, TUE, WED, THR, FRI, SAT, SUN }

inline fun <reified T: Enum<T>> mkString(): String = 
	buildstring {
    	for (v in enumValues<T>()) {
        	append(v)
            append(",")
        }
    }

mkString<DAYSOFWEEK>() // MON, TUE, WED, ...

```

`enumValues<T>()`를 활용해 제네릭 이넘 값에 접근할 수 있다. 역으로 이름에서 값을 가져오고 싶으면 `enumValuesOf`를 사용한다.


### mod와 rem

mod 대신 rem이 `%`연산자로 해석된다.

```
data class V(val value:Int) {
	infix operator fun rem(other:V) = V(10)
    infix operator fun mod(other:V) = V(-10)
}

val x = V(5)
val y = V(7)
val r1 = x % y // V(10)
val r2 = x mod y // V(-10)
val r3 = x rem y // V(10)
```
그 이유는 `BigInteger`구현과 다른 정수형 타입의 `%`연산 결과를 맞추기 위함이다. 

### 표준 라이브러리의 변화


### onEach()

컬렉션과 시퀀스에 `onEach` 확장 함수가 생겼다. `onEach`는 `forEach`와 비슷하지만 다시 컬렉션이나 시퀀스를 다시 반환하기에 메소드 연쇄 호출이 가능하다.

```
listOf(1,2,3,4,5).onEach { println("$it") }.map { it*it }.joinToString(",")
```

### takeIf

`takeIf`는 수신 객체가 술어를 만족하는지 검사해서 만족할 때 수신 객체를 반환하고, 불만족할 때 `null`을 반환한다. `takeUnless`는 이의 반대이다.

```
val srcOrKoltin: Any = File("src").takeIf { it.exists() } ?: File("Kotlin")
```


### Map.toMap()과 Map.toMutableMap()

맵을 복사할 때 사용한다.

```
val m1 = mapOf(1 to 2)
val m2 = m1.toMutableMap()
m2[10] = 100
println(m2) // { 1=2, 10=100 }
```

## 코틀린 1.2

### 어노테이션의 배열 리터널
어노테이션 `[]`사이에 원소를 넣어서 표시할 수 있다.
```
@RequestMapping(value = ["v1", "v2"], path = ["path", "to", "resource"])
```

### 지연 초기화 검사

```
lateinit var url: String

if(::url.isInitialized) { ... }
```


### 경고를 오류로 처리하기
커맨드라인 옵션에 `-Werror`를 지정하면 모든 경고를 오류로 처리한다. 그레이들에서는 다음과 같이 사용

```
complieKotlin {
	kotlinOptions.warningsAsErrors = true
}
```

### 스마트 캐스트 개선

```
val b = (x as? SubClass)?.subclassMethod1()

if(b!=null) {
	x.subclassMethod2() // x는 Subclass
}
```

람다 단에서`var`에 대한 스마트 캐스트가 가능하다. 단, 스마트 캐스트가 이뤄진 이후에는 `var`을 변경하면 안 된다.


### 가변 인자에게 이름 붙은 인자로 원소 하나만 넘기기

예전에는 `foo(items = i)`처럼 가변 인자 파라미터에 원소를 단 하나만 넘겨도 정상 처리됐다. 일관성을 위해 이런 경우 이제 스프레드 연산자를 사용해야한다.
```
foo(items = *intArrayOf(1))
```


## 코틀린 1.3

### Contract, 계약

```
fun String?.isNotNull(): Boolean = thjis != null

fun foo(s: String?) {
	if (s.isNotNull()) s.length // 스마트 캐스팅 X
}
```

널에 대한 검사를 다른 함수에서 진행하면 스마트 캐스팅이 진행되지 않았다.
코틀린1.3에서는 컨트랙트를 사용해 이런 상황을 개선할 수 있다. 

> 컨트랙트는 함수의 동작을 컴파일러가 이해할 수 있게 기술하기 위한 기능이다. 현재 두 가지 종류의 컨트랙트를 지원한다.


1. 함수의 반환 값과 인자 사이의 관계를 명시해서 스마트캐스트 분석을 쉽게 만들어주는 컨트랙트

```
fun require(condition: Boolean) {
	// 이 함수가 정상적으로 반환되면, condition이 참이다. 라는 조건을 표현하는 컨트랙트
    contraact { returns() implies condition }
	if (!condition) throew IllegalArgumentException(...)
}

fun foo(s: String?) {
	require(s is String)
    // s is String 이라는 조건이 참이면 예외가 발생하지 않음으로
    // 이하 코드에서 s 를 String으로 스마트캐스트하여 사용할 수 있다.
}
```


2. 고차 함수가 있을 때 컴파일러가 변수 초기화 여부 분석을 더 잘 할 수 있게 돕는 컨트랙트

```
fun synchronize(lock: Any?, block: () -> Unit) {
	// 이 함수는 block을 여기서 바로 실행하여 오직 한번만 실행한다는 뜻의 컨트랙트이다.
    contract { callsInPlace(block, EXACTLY_ONCE) }
}

fun foo() {
	val x: Int
    synchronize(lock) {
    	x = 52
    	// 이 블록을 한 번만 실행한다는 것을 컴팡일러가 알고 있음으로 val을 재 대입한다는 오류 메세지 표시 X
    }

	println(x)
}
```

### When의 대상을 변수에 포획

`when`의 대상을 변수에 대입할 수 있다.

```
fun Request.getBody() =
	when (val response = executeRequest()) {
    	is Success -> response.body
        is HttpError -> throw HttpException(response.status)
    }
```

물론 `when`바로 앞에서 변수에 식의 결과 값을 대입하고 `when`을 사용할 수도 있다. 하지만 이 예제처럼 `when`의 괄호 안에서 변수를 선언하고 대입할 수 있으면 `when`식 안에서만 사용할 수 있는 변수가 생기므로, `when`문 밖의 네임스페이스가 더럽혀지는 일을 줄일 수 있다.


### 파라미터 없는 메인

프로그램 시작점은 원래 `main(args: Array<String>)`처럼 문자열 배열을 파라미터로 받아야 했지만, `args`를 사용하지 않는 경우 파라미터를 받지 않는 메임 함수를 선언할 수 있다.

```
fun main() {
	println("Hello, world!")
}
```


### 함수 파라미터 수 제한 완화

파라미터 수를 255개까지 처리할 수 있다.
_너무 많은 파라미터를 사용하지는 말 것_


### 인라인 클래스(실험적 기능)

프로퍼티가 단 하나뿐인 클래스를 `inline`이라는 키워드를 사용해 인라인 클래스로 정의할 수 있다.

```
inline class Name(val s: String)
```

코틀린 컴파일러는 인라인 클래스를 사용하는 코드를 번역할 때 내부 프로퍼티의 값을 사용해 공격적으로 최적할 수 있다. 예를 들어 별도로 생성자 등을 만들지 않고 인라인 클래스의 인스턴스 객체 대신, 내부 프로퍼티 객체를 사용하게 코드를 생성하는 등의 최적화가 가능하다.

```
fun main() {

	// 아래 호출은 Name 클래스에 속한 인스턴스를 만들지 않고
    // `Kotlin`이라는 문자열만 만든다.
	val name = Name("Kotlin")
    // 다음 println문을 처리할 때 Name타입의 객체에 있는 필드에 접근해 문자열을 가져오는 대신 문자열에 바로 접근한다.
    println(name.s)
}
```

### 맵 연관 쌍 추가 함수 associateWith()

키 컬렉션과 값 컬렉션을 서로 `1:1`로 연관시킬 때 다음과 같이 사용할 수 있다.

```
val keys = 'a'...'f'
val map = keys.associateWith{ it.toString().repeat(5).capitalize() }
map.forEach { println(it) }
// a = Aaaaa
// b = Bbbbb
// c = Ccccc
// d = Ddddd
// e = Eeeee
```


# 코투린과 Async/Await

위키피디아에서의 코루틴의 정의는 다음과 같다.

> 코루틴은 컴퓨터 프로그램 구성 요소 중 하나로 비선점형 멀티태스킹을 수행하는 일반화한 서브루틴이다. 코루틴은 실행을 일시 중단하고 재게할 수 있는 여러 진입 지점을 허용한다.


서브루틴은 여러 명령어를 모아 이름을 부여해서 반복 호출할 수 있게 정의한 프로그램 구성 요소로, 다른 말로 함수라고 부르기도 한다.

코루틴이란 서로 협력해서 실행을 주고받으면서 작동하는 여러 서브루틴을 의미한다. 예를 들어 어떤 함수 A가 실행되다가 코루틴 B를 호출하면 A가 실행되던 스레드 안에서 코루틴 B의 실행이 시작된다. 코루틴 B는 실행을 진행하다가 실행을 A에 양보한다.(`yield`명령어를 사용하는 경우) A는 다시 코루틴을 호출햇떤 바로 다음 부분부터 실행을 계속 진행하다가 또 코루틴 B를 호출한다. 이때 B가 일반적인 함수라면 로컬 변수를 초기화하면서 처음부터 실행을 다시 시작하겠지만, 코루틴이면 이전에 `yiled`로 실행을 양보했던 지점부터 실행을 계속하게 된다.

## 코루틴 빌더

### kotlinx.coroutines.CoroutinScope.launch

`launch`는 코루틴을 잡으로 반환하며, 만들어진 코루틴은 기본적으로 즉시 실행된다. `Job`의 `cancel()`을 호출해 코루틴 실행을 중단시킬 수 있다. 

`launch`는 `CoroutineScope`객체가 블록의 `this`로 지정되어야 한다. (즉 `suspend`함수 내에서만 실행이 가능하다) 다음예를 보자

```
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import java.time.ZonedDateTime
import java.time.temporal.ChronoUnit

fun now() = ZonedDateTime.now().toLocalTime().truncatedTo(ChronoUnit.MILLIS)

fun log(msg: String) = println("${now()}:${Thread.currentThread()} : ${msg}")

fun main() {
    log("Main() started")
    launchInGlobalScope()
    log("launchInGlobalScope() excuted")
    Thread.sleep(2000L)
    log("main() terminated")
}

fun launchInGlobalScope() {
    GlobalScope.launch {
        log("coroutine started.")
    }
}


```

결과 
```
11:28:46.646:Thread[main,5,main] : Main() started
11:28:46.693:Thread[main,5,main] : launchInGlobalScope() excuted
11:28:46.693:Thread[DefaultDispatcher-worker-2,5,main] : coroutine started.
11:28:48.693:Thread[main,5,main] : main() terminated
```

위의 예에서는 `GlobalScope.launch`로 만들어낸 코루틴이 서로 다른 스레드에서 실행된다는 점이며, `GloablScope`는 메인 스레드가 실행 중인 동안만 동작을 보장한다. 즉 `Thread.sleep`을 없애면 코루틴이 아예 실행되지 않는다. 

이를 방지하기위해 `runBlocking()`을 사용할 수 있다. 이는 `CoroutineScope`의 확장 함수가 아닌 일반함수에서 코루틴의 실행이 끝날 때까지 현재 스레드를 블록시킨다.

```
fun main() = runBlocking {
    log("Main() started")
    launch {
        launchInGlobalScope("Coroutine1", 300)
    }
    launch {
        launchInGlobalScope("Coroutine2", 0)
    }
    log("main() terminated")
}

suspend fun launchInGlobalScope(msg: String, delayTime: Long) {
    log("$msg started.")
    delay(delayTime)
    log("$msg ended.")
}
```

결과

```
11:39:49.243:Thread[main,5,main] : Main() started
11:39:49.249:Thread[main,5,main] : main() terminated
11:39:49.250:Thread[main,5,main] : Coroutine1 started.
11:39:49.254:Thread[main,5,main] : Coroutine2 started.
11:39:49.254:Thread[main,5,main] : Coroutine2 ended.
11:39:49.558:Thread[main,5,main] : Coroutine1 ended.
```

`runBlocking`에서의 쓰레드는 모두 `main`쓰레드에서 동작하며

> `runBlocking`은 코루틴에서 사용해서는 안된다고 권장하고 있으며 suspend함수의 도메인 로직 테스트용으로만 쓰이도록 설계되었다. 또한 runBlocking의 경우는 eventLoop를 활용하여 task들을 큐로 관리한다.


### kotlinx.coroutines.CoroutineScope.async

`async`는 `Deffered`를 반환하며 이는 `Job`을 상속한 클래스이기 떄문에 `launch`대신 `async`를 사용해도 항상 아무 문제가 없다. 

즉 `Job` == `Defferd<Unit>`이라고 생각할 수도 있다.

```
fun main() = runBlocking {
    val d1 = async { delay(1000L); 1 }
    log("after async(d1)")
    val d2 = async { delay(2000L); 2 }
    log("after async(d2)")
    val d3 = async { delay(3000L); 3 }
    log("after async(d3)")

    log("${d1.await() + d2.await() + d3.await()}")
    log("after await all & add")
}
```

결과

```
11:51:43.058:Thread[main,5,main] : after async(d1)
11:51:43.062:Thread[main,5,main] : after async(d2)
11:51:43.062:Thread[main,5,main] : after async(d3)
// 3초 후
11:51:44.072:Thread[main,5,main] : 6
11:51:44.072:Thread[main,5,main] : after await all & add
```

순서대로 실행해야 했다면 6초이상이 걸리지만, 3초내 모든 작업을 수행함을 볼 수 있다. 쓰레드를 여럿 사용하는 병렬 처리와 달리 모든 `async`함수들이 메인 스레드 안에서 실행됨을 볼 수 있다. 

쓰레드의 개수가 한정된 경우 하나의 쓰레드에서의 병렬처리가 가능한 코루틴은 빛을 발휘할 것이다.

## 코루틴 컨텍스트와 디스패쳐

`launch`, `async`등은 모두 `CoroutineScope`의 확장 함수이다. 그런데 `CoroutineScope`에는 `CoroutineContext` 타입의 필드 하나만 들어있다. `CoroutineScope`는 `CoroutineContext`필드를 `launch`등의 확장 함수 내부에서 사용하기 위한 매개체 역할만을 담당한다. 원한다면 `launch`등에 `CoroutineContext`를 넘길 수도 있다는 점에서 실제로 `CoroutineScope`보다 `CoroutineContext`가 코루틴 실행에 더 중요한 의미가 있음을 유추할 수 있을 것이다.

> `CoroutineContext`는 실제로 코루틴이 실행 중인 여러 작업(`job`타입)과 디스패쳐를 저장하는 일종의 맵이라 생각할 수 있다.

코틀린 런타임은 이 `CoroutineContext`를 사용해서 다음에 실행할 작업을 선정하고, 어떻게 스레드에 배정할지 대한 방법을 결정한다. 다음예를 보자.
```
fun main() = runBlocking {
    launch(Dispatchers.IO) {
        log("run On IO Thread")
    }
    launch(Dispatchers.Default) {
        log("run On Default Thread")
    }
    launch(Dispatchers.Unconfined) {
        log("run On Unconfined Thread")
    }
}
```

같은 `launch`를 사용하더라도 전달하는 컨텍스트에 따라 서로 다른 스레드상에서 코루틴이 실행됨을 알 수 있다.


### 일시 중단 함수와 빌더에 대해

`launch`, `async`, `runBlocking`은 모두 코루틴 빌더이다. 이들은 코루틴을 만들어 준다.

`delay()`와 `yield()`는 일시 중단 함수라고 부른다. 이외에도 다음과 같은 함수가 있다.

* `withContext` 다른 컨텍스트로 코루틴을 전환한다.

* `withTimeOut` 코루틴이 정해진 시간 안에 실행되지 않으면 예외를 발생시킨다.

* `withTimeoutOrNull` 코루틴이 정해진 시간 안에 실행되지 않으면 `null`을 결과로 반환한다.

* `awaitAll` 모든 작업의 성공을 기다린다. 작업 중 하나가 예외로 실패하면 이또한 실패한다.

* `joinAll` 모든 작업이 끝날 때까지 현재 작업을 중단시킨다.

코루틴내부에서 사용할 수 있는 중단함수는 어떤 동작이 필요한가??

1. 코루틴에 진입할 떄와 코루틴에서 나갈 때 코루틴이 실행 중이던 상태를 저장하고 복구하는 등의 작업을 할 수 있어야 한다.

2. 현재 실행 중이던 위치를 저장하고 다시 코루틴이 재개될 때 해당 위치로부터 실행을 재개할 수 있어야 한다.

3. 다음에 어떤 코루틴을 실행할지 결정한다.


세가지 중 마지막 동작은 코루틴 컨텍스트에 있는 디스패처에 의해 수행된다. `suspend`함수를 컴파일 하는 컴파일러는 앞의 두 가지 작업을 할 수 있는 코드를 생성해내야 한다. 이때 코틀린은 `컨티뉴에이션 패싱 스타일 변환(CPS)`과 상태기계를 활용해 코드를 생성해 낸다.

`CPS`변환은 프로그램의 실행 중 특정 시점 이후에 진행해야 하는 내용을 별도의 함수로 뽑고(이런 함수를 컨티뉴에이션이라 부른다.) 그 함수에게 현재 시점까지 실행한 결과를 넘겨서 처리하게 만드는 소스코드 변환 기술이다. 

`CPS`를 사용하는 경우 프로그램이 다음에 해야 할 일이 항상 컨티뉴에이션이라는 함수의 형태로 전달되므로, 나중에 할일을 명확히 알 수 있고, 그 컨티뉴에이션에 넘겨야 할 값이 무엇인지도 명확하게 알 수 있기 때문에 프로그램이 실행 중이던 특정 시점의 맥락을 잘 저장했다가 필요할 떄 다시 재개할 수 있다. 콜백함수와 유사한 느낌이다.

```
suspend fun example(v: Int): Int {
	return v*2;
}
```
코틀린 컴파일러는 이 함수를 컴파일하면서 뒤에 Continuation을 인자로 만들어 붙여준다.
```
public static final Obejct example(int v, @Notnull Continuation var1)
```

이 함수를 호출할 때는 함수 호출이 끝난 후 수행해야 할 작업을 `var1`으로 전달하고, 함수 내부에서는 필요한 모든 일을 수행한 다음에 결과를 `var1`에 넘기는 코드를 추가한다.


#### 코루틴 빌더를 직접 만드는 방법은 내용이 어려워서 패스,,, 이 쪽을 충분히 이해하지 못하더라도 `launch`, `async`, `await`정도의 기본 제공 코루틴 빌더만으로 충분히 코딩이 가능하다.


---

# 책을 읽으며

![](https://velog.velcdn.com/images/cksgodl/post/b0082e8c-c375-4f90-8f04-605b6be584e4/image.png)

#### 타켓 층

이 책 또한 어느정도 자바 경험이 있는 개발자를 주요 대상으로 한다. 코틀린과 `JVM`의 상호작용의 복잡한 측면을 계속하여 이야기하는데 책을 이해하기 위한 공부가 필요하다.


#### Effective Kotlin과의 비교

내용의 량은 `Kotlin In Action`이 더 많고 근본있지만, 내용의 질과 가성비는 `Effective Kotlin`더 높은 것 같다. 

`코틀린 인 액션`은 코틀린에 대한 규칙, 정보, 특성을 모두 알려주는 느낌이면 비교적 최근에 나온 `이펙티브 코틀린`은 `코틀린 인 액션`에서 제공하는 내용을 어떻게 사용하면 좋을지 공식처럼 알려주는 느낌이다.


#### 리뷰 및 느낀점

나는 정말 간단하게 읽고 넘어간 책이지만(책의 내용이 너무 자세함), 자바와 코틀린의 차이와 코틀린의 특성을 깊게 공부하기 위해 좋은 책이다.

하지만 책의 출판년도가 17년도이며 책 내부에서는 코틀린 1.3업데이트 까지 다루고 있지만, 현재는 코틀린 1.8버전까지 나왔기에 내용 자체가 좋게 말하면 근본이 있지만, 오래된 소스도 많다.(직접 예제를 쳐보는데 Deprecated된 메소드라고 떠서 이게 맞나?? 라는 생각이 든 예제가 몇개 있다.)

전공책을 느끼며 항상 느끼는 점은 내용이 어렵다. 이 책은 더 어렵다. 어노테이션 부분, 코루틴의 빌더함수를 직접만드는 부분등은 내 수준으로는 도저히 이해가 안되서 그냥 넘어갔다. 후에 좀 더 공부하고 복수하러 돌아와야 겠다.

600페이지 가량으로 코틀린에 대해 설명하는데 내용이 너무 자게하고 또 복잡하다. 코틀린을 곱씹어 먹을 예정이라면 추천하지만, 입문하거나 간단하게 살펴보기엔 적당하지 않은 책이다. 

> 자세하고 복잡하지만 코틀린의 근본에 대해 배울 수 있는 책






