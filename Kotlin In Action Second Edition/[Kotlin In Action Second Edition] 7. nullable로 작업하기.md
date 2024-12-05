`Kotlin` 코드의 안정성을 개선하는 데 도움이 되는 `Kotlin`의 필수 기능 중 하나는 `null` 가능 유형에 대한 지원이다.

## 7.1 NullPointerException없이 작업하기

런타임에 발생하는 `NPE`는 사용자와 개발자 모두에게 번거로운 문제이다. `Kotlin`을 비롯한 최신 언어의 접근 방식은 이러한 문제를 런타임 오류에서 컴파일 시간 오류로 전환하는 것이다.

코틀린은 `nullable`한 언어가 아님으로 이를 컴파일 시점에서 회피한다.

## 7.2 `nullable`은 명시적으로 표시해야 한다.

`Kotlin`은 널가능 유형을 명시적으로 표현해야 한다. 

```kotlin
fun strLenSafe(s: String?) = ...
```

`?`를 활용해 널 참조 유형임을 나타낼 수 있다.

```kotlin
fun main() {
    val x: String? = null
    var y: String = x
    // ERROR: Type mismatch:
    // inferred type is String? but String was expected
}
```
![](https://velog.velcdn.com/images/cksgodl/post/db514c0a-5339-4d9a-aff8-b634f1f1e7ae/image.png)

## 7.3 타입의 의미 자세히 살펴보기

`String` 타입의 변수가 있다고 하자. `Java`에서 이러한 변수는 두 가 지 종류의 값, 즉 `String` 클래스의 인스턴스 또는 `null` 중 하나를 저장할 수 있다. 이러한 종류의 값은 서로 완전히 다르다. `Java`의 자체 인스턴스 연산자조차도 `null`이 `String`이 아님을 알려준다. 변수 값에 대해 수행할 수 있는 연산도 완전히 다르다. 

이는 `Java`의 타입 시스템이 제대로 작동하지 않는다는 것을 의미한다. 변수에 선언된 유형(문자열)이 있더라도 추가 검사를 수행하지 않으면 이 변수의 값으로 무엇을 할 수 있는지 알 수 없다. 이에따라 가끔 잘못된 판단으로 인해 프로그램이 `NullPointerException`과 함께 충돌하는 경우가 있다.

> Java에서 NPE에 대응하기
>
> @Nullable, @NotNull을 활용하여 NPE를 유연하게 대응할 수 있다. 또는 `Optional`유형을 활용하여 값을 표현할 수도 있다. 하지만, 이는 코드를 더 장황하게 만들고, 런타임 성능에 영향을 끼친다.

참고) 코틀린에서의 런타임에 널러블 타입이나 널러블이 아닌 타입의 객체는 동일하며, 널러블 타입은 널러블이 아닌 타입의 래퍼가 아니다. 따라서 성능에 거의 영향을 미치지 않는 내재적 검사(https://kotlinlang.org/docs/java-to-kotlin-nullability-guide.html#support-for-nullable-types)를 제외하면 Kotlin에서 nullable 유형으로 작업하는 것은 기본적으로 런타임 오버헤드가 없다.

## 7.4 널 검사와 메서드 호출을 안전 하게, 안전 호출 연산자 "?."

아래 두 연산은 동일하게 작동한다.

```kotlin
str?.uppercase()
if (str != null) str.uppercase() else null.
```
![](https://velog.velcdn.com/images/cksgodl/post/f01cceff-e806-4007-b1a2-897311ed523c/image.png)


## 7.5 엘비스 연산자를 사용하여 널 케이스에 기본값 제공 "?:"

코틀린에서는 null케이스에서 elvis연산자를 대해 기본값을 제공할 수 있다. 이는 `null-coalescing`라고 불리기도 한다.

```kotlin
fun greet(name: String?) {
    val recipient: String = name ?: "unnamed"
    println("Hello, $recipient!")
}
```

> Elvis어원의 뜻은 엘비스의 머리스타일이라고 한다. 
>
> ![](https://velog.velcdn.com/images/cksgodl/post/c4fbf39e-5a08-425e-8f53-983e8b7c1a74/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/5024b485-efac-4e1f-97bc-0a2040d9beb3/image.png)

`Kotlin`에서 `Elvis` 연산자가 특히 편리한 이유는 `return` 및 `throw`와 같은 연산이 표현식으로 작동하므로 연산자의 오른쪽에 사용할 수 있다는 점이다. 

```kotlin
val address = person.company?.address
      ?: throw IllegalArgumentException("No address")
```

## 7.6 예외를 던지지 않고 안전하게 캐스팅: "as?"

`as`는 값을 형변환하려는 유형이 없는 경우 `ClassCastException`을 `throw`한다. 물론 `is` 검사와 결합하여 올바른 유형이 있는 지 확인할 수 있다. 하지만 안전하고 간결한 언어로서 `Kotlin` 더 나은 솔루션인 `as?`를 제공한다.

![](https://velog.velcdn.com/images/cksgodl/post/e08ce47e-5d2b-45e3-8831-c7c15a326812/image.png)

```kotlin
 override fun equals(other: Any?): Boolean {
        val otherPerson = other as? Person ?: return false
        return otherPerson.firstName == firstName &&
                otherPerson.lastName == lastName
}
```

## 7.7 non-null assertion 연산자를 사용하여 컴파일러에 약속하기

`non-null assertion`은 가장 간단하고 쉽게 널을 처리하는 도구이다. 이 어설션은 이중 느낌표(!!)로 표시되며 모든 값을 `null` 가능하지 않은 유형으로 변환한다. 이 때 `null` 값의 경우 예외가 발생한다. 

![](https://velog.velcdn.com/images/cksgodl/post/2b088785-30ff-47b7-8b9c-e3cf352451d7/image.png)

```kotlin
fun ignoreNulls(str: String?) {
    val strNotNull: String = str!!
    println(strNotNull.length)
}

fun main() {
    ignoreNulls(null)
    // Exception in thread "main" java.lang.NullPointerException
    //  at <...>.ignoreNulls(07_NotnullAssertions.kt:2)
}
```

이는 컴파일러에게 "나는 값이 null이 아니 라는 것을 알고 있으며, 내가 틀린 것으로 판명되면 예외를 처리할 준비가 되어 있다."라고 말하는 것과 동일하다.

> 참고 
> 
> 느낌표 두 개가 약간 무례해 보일 수 있다. 마치 컴파일러에게 소리를 지르는 것 같은 느낌표이기도 하다. 하지만 이는 의도적인 것이다. 컴파일러가 검증할 수 없는 주장을 하지 않는 더 나은 솔루션으로 사용자를 유도하기 위한 것이다.

## 7.8 nullable 가능한 표현식 다루기: "let"

세이프 콜 연산자와 함께 사용하면 하나의 간결한 표현식으로 표현식을 사용하여, 그 결과가 `null`인지 확인하고, 그 결과를 변수에 저장하는 작업을 모두 수행할 수 있다.

```kotlin
fun sendEmailTo(email: String) { /*...*/ }
        
 fun main() {
	val email: String? = "foo@bar.com"
	sendEmailTo(email)
	//ERROR: Type mismatch: inferred type is String? but String was expected
    
    // should 
    if (email != null) sendEmailTo(email)
    
    // better
    email?.let { email -> sendEmailTo(email) }
}
```

![](https://velog.velcdn.com/images/cksgodl/post/1376c4ea-03f9-44d5-a1b3-b453a1ffa7e1/image.png)

> 여러 지역함수 비교하기
>
> ![](https://velog.velcdn.com/images/cksgodl/post/cd66c68d-284c-4d9a-9240-bf3436eec00e/image.png)

## 7.9 즉시 초기화되지 않고 널이 아닌 타입을 선언하기: Late-initialized 

코틀린에서는 일반적으로 생성자에서 모든 속성을 초기화해야 하며, 속성에 널이 아닌 유형이 있는 경우 널 이 아닌 이니셜라이저 값을 제공해야 한다. 해당 값을 제공할 수 없는 경우 대신 널 가능 유형을 사용해야 한다. 이렇게 하면 프로퍼티에 액세스할 때마다 `null` 검사 또는 `!!` 연산자가 필요하게 된다.

이때는 코틀린의 지연초기화를 활용할 수 있다.

```kotlin
class MyService {
    fun performAction(): String = "Action Done!"
}

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class MyTest {
    private lateinit var myService: MyService

	@BeforeAll fun setUp() {
    	myService = MyService()
	}

	@Test fun testAction() {
    	assertEquals("Action Done!", myService.performAction())
	}
}
```

생성자 외부에서 값을 변경할 수 있어야 하고, 생성자에서 초기화해야 하는 `final` 필드로 컴파일되기 때문에 늦게 초기화된 프로퍼티는 항상 `var`이라는 점에 유의하자.

프로퍼티가 초기화되기 전에 프로퍼티에 액세스하면 다음과 같은 결과가 표시된다.

```kotlin
kotlin.UninitializedPropertyAccessException:
    lateinit property myService has not been initialized
```

![](https://velog.velcdn.com/images/cksgodl/post/1288b41c-588c-4a7f-bdc6-65440dcc10f9/image.png)


> 참고
>
> `lateinit`은 클래스의 프로퍼티에만 국한되지 않는다. 함수 본문이나 람다 내부의 로컬 변수와 최상위 프로퍼티를 늦게 초기화하도록 지정할 수도 있다.


## 7.10 세이프콜 없이 nullable타입  확장하기

![](https://velog.velcdn.com/images/cksgodl/post/62f652c7-cbf5-4f4f-a982-eb94dfdf0f65/image.png)

위의 예시처럼 nullable 타입이여도 확장함수를 통해 안전하게 처리할 수 있다.

코틀린에서는 다양한 null처리 확장함수를 제공한다. (ifBlank, ifEmpty, etc...)

```kotlin
fun String?.isNullOrBlank(): Boolean = this == null || this.isBlank()
```

```kotlin
fun sendEmailTo(email: String) {
    println("Sending email to $email")
}

fun main() {
    val recipient: String? = null
    recipient.let { sendEmailTo(it) }
    // ERROR: Type mismatch:
    // inferred type is String? but String was expected
}
```

## 7.11 Nullability of type parameters

코틀린의 기본 유형은 모두 nullable이다. 제너릭의 경우는 물음표로 끝나지 않아도 nullable이다.

```kotlin
fun <T> printHashCode(t: T) {
    println(t?.hashCode())
}

fun main() {
    printHashCode(null)
    // null
}
```

유형 매개변수를 널링할 수 없도록 만들려면 널링할 수 없는 상한을 지정해야 한다. 이렇게 하면 null 가능한 값을 인수로 사용할 수 없다.

```kotlin
fun <T: Any> printHashCode(t: T) { 
	println(t.hashCode())
}

fun main() {
    printHashCode(null)
    // Error: Type parameter bound for `T` is not satisfied
    printHashCode(42)
    // 42
}
```

## 7.12 자바에서의 Nullability 

자바와 코틀린을 동시에 사용하게 된다면 null 유형에 대한 처리가 다음과 같이 진행된다.

앞서 언급했듯이 `Java` 코드에는 어노테이션을 사용하여 표현되는 `nullable` 가능성에 대한 정보를 표현한다. 이 정보가 코드에 있으면 `Kotlin`은 이를 사용한다. 따라서 `Java`의 `@Nullable String`은 `Kotlin`에서 `String?` 로 표시되고 `@NotNull String`은 그냥 String으로 표시된다.

![](https://velog.velcdn.com/images/cksgodl/post/a99f75d9-673c-42c5-980b-6b4a0f9cd056/image.png)

### 7.12.1 플랫폼 유형

플랫폼 유형은 기본적으로 Kotlin에 널 가능성 정보가 없는 유형이다. Java에서와 마찬가지로 해당 유형으로 모든 연산을 허용한다. 따라서 NPE가 발생할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/b8339f8a-3f1a-4bc4-9258-0784160f1d88/image.png)

따라서 Java API로 작업할 때는 주의하자. 대부분의 라이브러리에는 주석이 달려 있지 않으므로 모든 타입을 `null`이 아닌 것으로 해석할 수 있고, 이로 인해 오류가 발생할 수 있다. 오류를 방지하려면 사용중인 `Java` 메서드의 설명서(및 필요한 경우 구현)를 확인하여 언제 `null`을 반환할 수 있는지 확인하고 해당 메서드에 대한 확인을 추가해야 한다.

### 7.12.2 상속

`Kotlin`에서 `Java` 메서드를 재정의할 때 매개 변수와 반환 유형을 널 가능으로 선언할지, 아니면 널 불가능으로 선언할지 선택할 수 있다.

```kotlin
/* Java */
interface StringProcessor {
	void process(String value);
}

// Kotlin에서는 다음 두 가지 구현이 모두 컴파일러에서 허용됩니다.
class StringPrinter : StringProcessor {
    override fun process(value: String) {
		println(value)
    }
}

class NullableStringPrinter : StringProcessor {
	override fun process(value: String?) {
    	if (value != null) {
        	println(value)
		} 
    }
}
```

## 요약

- Kotlin의 널 가능 유형 지원은 런타입 시 발생할 수 있는 `NullPointerException` 오류를 컴파일시점으로 회피한다.
- 일반유형은 명시적으로 널가능으로 표시되지 않는 한 기본적으로 널불가능 하다. 유형 이름 뒤에 물음표가 붙으면 해당 유형이 무효화 가능함을 나타낸다.
- Kotlin은 널러블 타입을 간결하게 처리하기 위한 다양한 도구를 제공한다.
- 안전 호출(?.)을 사용하면 메서드를 호출하고 널 가능 객체의 프로퍼티에 액세스할 수 있습.
- `Elvis 연산자(?:)`를 사용하면 null일 수 있는 표현식의 기본값을 제공하거나, 실행에서 반환하거나, 예외를 던질 수 있다.
- 널이 아닌 어설션(!!)을 사용하여 주어진 값이 널이 아님을 컴파일러에 약속할 수 있다. (하지만 예외를 예상해야 한다).
- `let scope` 함수는 호출되는 객체를 람다의 매개변수로 바꾼다. 이 함수는 안전 호출 연산자와 함께 널 가능 타입의 객체를 널 가능하지 않은 타입의 객체로 효과적으로 변환한다.
- as? 연산자는 값을 유형으로 캐스팅하고 다른 유형을 가진 경우를 처리하는 쉬운 방법을 제공한다.
