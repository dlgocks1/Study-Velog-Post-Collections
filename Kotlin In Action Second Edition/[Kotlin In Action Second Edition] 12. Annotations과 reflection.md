
함수를 호출하려면 함수가 정의된 클래스와 이름 및 매개변수 유형을 알아야 한다. 어노테이션과 리플렉션은 이를 뛰어넘어 미리 알 수 없는 임의의 클래스를 다루는 코드를 작성할 수 있는 기능을 제공한다.

## 12.1 어노테이션 선언 및 적용

어노테이션을 사용하면 추가 메타데이터를 선언과 연결할 수 있다. 그러면 어노테이션이 구성된 방식에 따라 소스 코드, 컴파일된 클래스 파일 또는 런타임에 작동 하는 도구에서 메타 데이터에 액세스할 수 있다.

예제로 `@Deprecated` 어노테이션을 살펴보자. `Deprecated` 어노테이션에는 최대 3개의 매개변수가 사용된다. 사용 중단 이유를 설명하는 메시지, 선택 사항인 `replaceWith` 매개변수, 사용 중단 수준(`WARNING`, `ERROR`) 등

```kotlin
@Deprecated("대신 removeAt(index)를 사용하세요.", ReplaceWith("removeAt(index)")) 
fun remove(index: Int) { /* ... */ }
```
![](https://velog.velcdn.com/images/cksgodl/post/b0d0fe05-3ac6-4d38-b115-b231c8637183/image.png)

위처럼 어노테이션은 `IDE`에 추가적인 정보도 제공할 수 있다.

어노테이션에는 기본 유형, 문자열, 리스트, 클래스 참조, 기타 어노테이션 클래스 및 그 배열의 매개변수만 가질 수 있다. 어노테이션 인수를 지정하는 구문은 다음과 같다:

- 클래스를 주석 인수로 지정하기 - 클래스 이름 뒤에 ::클래스를 넣습니다: `MyAnnotation(MyClass::class)`. 
  - 예를 들어, 직렬화 라이브러리(이 장의 뒷부분에 서 설명하겠지만)는 역직렬화 프로세스 중에 사용되는 인터페이스와 구현 간의 매핑을 설정하기 위해 클래스를 인수로 기대하는 어노테이션을 제공할 수 있다
- 다른 어노테이션을 인수로 지정하기
- 배열을 인수로 지정하기 - 괄호를 사용할 수 있다: 
   - 요청매핑(경로 = `["/foo",
"/bar"]`) 또는 `arrayof` 함수를 사용하여 배열을 지정할 수도 있다. (Java로선 언된 어노테이션 클래스를 사용하는 경우 필요한 경우 value 매개변수가 자동으로 vararg 매개변수로 변환.)

어노테이션 인수는 컴파일 시점에 알 수 있어야 하므로 임의의 프로퍼티를 인자로 참조할 수 없다. 프로퍼티를 어노테이션 인수로 사용하려면 컴파일러에 해당 프로퍼티가 `const` 수정자로 표시해야 한다.

```kotlin
const val TEST_TIMEOUT = 10L
class MyTest {
    @Test
    @Timeout(TEST_TIMEOUT)
    fun testMethod() {
		// ... }
	}
}
```

### 12.1.2 어노테이션이 참조하는 정확한 선언을 지정: 어노테이션 Target

대부분의 경우 `Kotlin` 소스 코드에서 단일 선언이 여러 개의 `Java` 선언을 생성하며, 각 선언에는 어노테이션이 포함될 수 있다. 예를 들어 `Kotlin` 프로퍼티는 `Java` 필드, 게터, 설정자 및 해당 매개 변수에 해당할 수 있다. 따라서 이러한 요소 중 어떤 요소에 주석을 달아야 하는지 지정해야 할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/ee257191-5e5e-46e7-a89e-b0d91372b67a/image.png)

```kotlin
@JvmName("performCalculation")
fun calculate(): Int {
    return (2 + 2) - 1
}
```

자바에서는 `performCalculation`이 수행된다.

`Kotlin`의 프로퍼티에서도 동일한 작업을 수행할 수 있다. `Kotlin` 프로퍼티는 자동으로 게터와 세터를 정의한다. 속성의 게터 또는 세터에 `@JvmName` 어노테이션을 명시적으로 적용하려면 각각 `@get:JvmName()` 및 `@set:JvmName()`을 사용한다.

```kotlin
clss CertificateManager {
    @get:JvmName("obtainCertificate")
    @set:JvmName("putCertificate")
    var certificate: String = "-----BEGIN PRIVATE KEY-----"
}

class Foo {
    public static void main(String[] args) {
        var certManager = new CertificateManager();
        var cert = certManager.obtainCertificate();
        certManager.putCertificate("-----BEGIN CERTIFICATE-----");
}
```

`Kotlin`에서 정의된 어노테이션의 경우 속성에 직접 적용될 수 있도록 어노테이션을 선언할 수도 있다.

지원되는 어노테이션 전체 목록은 다음과 같다:

- `property` — Property (Java annotations can’t be applied with this use-site target) 
- `field` — Field generated for the property
- `get` — Property getter
- `set` — Property setter
- `receiver` — Receiver parameter of an extension function or property
- `param` — Constructor parameter
- `setparam` — Property setter parameter
- `delegate` — Field storing the delegate instance for a delegated property
- `file` — Class containing top-level functions and properties declared in the file

`Kotlin`에서는 클래스 및 함수 선언이나 유형뿐만 아니라 임의의 표현식에도 주석을 적용할 수 있다. 가장 일반적인 예는 주석이 지정된 표현식의 컨텍스트에서 특정 컴파일러 경고를 억제하는 데 사용할 수 있는 `@Suppress` 어노테이션이다.

```kotlin
fun test(list: List<*>) { 
	@Suppress("UNCHECKED_CAST")
	val strings = list as List<String> // ...
}
```

### 12.1.3 어노테이션을 사용하여 JSON 직렬화 사용자 지정하기

객체 직렬화를 제공하는 `JKid`의 구현에 대해 설명한다. 모든 코드는 쉽게 읽을 수 있을 정도로 작기에 한번쯤 읽어보는 것을 추천한다.

- [kotlin-in-action-2e-jkid](https://github.com/Kotlin/kotlin-in-action-2e-jkid)

```kotlin
data class Person(val name: String, val age: Int)

fun main() {
	val person = Person("Alice", 2e) println(serialize(person))
	// {"age": 2e, "name": "Alice"}
}
```

![](https://velog.velcdn.com/images/cksgodl/post/d1679463-c1de-4a5d-ad44-c252d21a710c/image.png)


어노테이션을 사용하여 객체가 직렬화 및 역직렬화되는 방식을 사용자 지정할 수 있다.

이 섹션에서는 두 가지 어노테이션인 `@JsonExclude`와 `@JsonName`에 대해 설명 하며, 이 장의 뒷부분에서 그 구현을 볼 수 있다:
- `JsonExclude` 어노테이션은 직렬화 및 역직렬화에서 제외해야 하는 프로퍼티를 표시하는 데 사용된다.
- `JsonName` 어노테이션을 사용하면 속성을 나타내는 키-값 쌍의 키가 속성 이름이 아닌 지정된 문자열이 되도록 지정할 수 있다.

```kotlin
data class Person(
    @JsonName("alias") val firstName: String,
    @JsonExclude val age: Int? = null
)
```

![](https://velog.velcdn.com/images/cksgodl/post/fbb43a83-71f9-45b3-9708-498af516f303/image.png)

### 12.1.4 나만의 어노테이션 선언 만들기

`JsonExclude` 어노테이션은 매개 변수가 없기 때문에 가장 간단한 형태이다. 아래와 같이 선언할 수 있다.

```kotlin
annotation class JsonExclude
```

어노테이션 클래스는 선언 및 표현식과 연관된 메타데이터의 구조를 정의하는 데만 사용되므로 코드를 포함할 수 없다. 따라서 컴파일러는 어노테이션 클래스에 대한 본문을 금지한다.

매개변수가 있는 어노테이션의 경우 매개변수는 클래스의 기본 생성자로 선언한다. 일반적인 기본 생성자 선언 구문을 사용하고 모든 매개 변수를 `val`로 표시 한다.

```kotlin
annotation class JsonName(val name: String)
```

### 12.1.5 메타 어노테이션: 어노테이션 처리 방법을 제어하기

`Kotlin` 어노테이션 클래스 자체에 어노테이션을 달 수 있다. 어노테이션 클래스에 적용할 수 있는 어노테이션을 메타 어노테이션이라고 한다. 표준 라이브러리에서는 여러가지 메타 어노테이션을 정의한다. 대표적인 예로써는 `@Target`이다.

```kotlin
@Target(AnnotationTarget.PROPERTY)
annotation class JsonExclude
```

`Target` 메타 어노테이션은 어노테이션을 적용할 수 있는 요소의 유형을 지정한다. 이를 사용하지 않으면 어노테이션이 모든 선언에 적용될 수 있다. 

`AnnotationTarget` 열거형의 값 목록은 어노테이션에 대해 가능한 모든 타겟을 제
공한다. 여기에는 클래스, 파일, 함수, 프로퍼티, 속성 액세스, 유형, 모든 표현식 등이
포함됩니다. 필요한 경우 여러 개의 타깃을 선언할 수 있다:

```kotlin
@Target(AnnotationTarget.CLASS, AnnotationTarget.METHOD)
```

자신만의 어노테이션 메타를 선언하려면 `ANNOTATION_CLASS`를 사용한다.

```kotlin
@Target(AnnotationTarget.ANNOTATION_CLASS)
annotation class BindingAnnotation

@BindingAnnotation
annotation class MyBinding
```

> 자바의 Retention 주석
>
> Java에서는 또 다른 중요한 메타 주석을 보았을 것이다. -> `Retention` 이를 사용하여 선언한 어노테이션을 `.class` 파일에 저장할지 여부와 런타임에 리플렉션을 통해 액세스할 수 있는지 여부를 지정할 수 있다. 
>
> Java는 기본적으로 `.class` 파일에 어노테이션을 유지하지만 런타임에 액세스할 수 있도록 하지는 않는다. 즉, 기본적으로 `Java`의 어노테이션은 컴파일시 `.class` 파일에서 직접 작업하는 프로그램에서만 접근할 수 있다. 일반적으로 대부분의 어노테이션은 런타임에 표시되어야 하므로 `Kotlin`에서 는 기본값이 다르다. 어노테이션은 런타임에 보존된다. 즉, 어노테이션에 명시적으로 액세스 할 수 있다.


### 12.1.6 클래스를 어노테이션 파라미터로 전달하여 동작을 추가로 제어하기

`const` 데이터를 인수로 보유하는 어노테이션을 정의하는 방법을 살펴봤지만 때로는 클래스의 메타데이터를 참조하는 기능이 필요할 때가 있다. 이를 위해 클래스 참조를 매개변수로 포함하는 어노테이션 클래스를 선언하면 된다.

`@DeserializeInterface`의 예를 보자, 해당 어노테이션이 있는 프로퍼티의 역직렬화를 제어할 수 있다. 해당 어노테이션을 활용해 역직렬화 중에 생성된 구현으로 어떤 클래스를 사용할지 지정할 수 있다.

```kotlin
interface Company {
    val name: String
}

data class CompanyImpl(override val name: String) : Company
data class Person(
    val name: String,
    @DeserializeInterface(CompanyImpl::class) val company: Company
)
```

역직렬화 시 `JKid`는 `Person` 인스턴스에 대해 중첩된 회사 객체를 읽을 때마다 `CompanyImpl` 인스턴스를 생성하고 역직렬화하여 회사 프로퍼티에 저장한다. 이를 지정하려면 `@DeserializeInterface` 어노테이션의 인수로 `CompanyImpl::class`를 사용한다.

```kotlin
annotation class DeserializeInterface(val targetClass: KClass<out Any>)
```

`KClass`유형은 `Kotlin`클래스에 대한 참조를 보유하는데 사용된다.

`out` 없이 `KClass<Any>`를 작성했다면 `CompanyImpl::class`를 인수로 전달 할 수 없으며, 허용되는 유일한 인수는 `Any::class`일 것이다.
  
![](https://velog.velcdn.com/images/cksgodl/post/405b7c21-d423-41c0-a06f-2f2eefaab965/image.png)

### 12.1.7 어노테이션 매개변수로서의 제네릭 클래스

`JKid`는 프로퍼티를 중첩된 객체로 직렬화한다. 하지만 이 동작을 변경하여 일부 값에 대해 고유한 직렬화 로직을 제공할 수 있다.

`@CustomSerializer` 어노테이션은 `CustomSerializer` 클래스에 대한 참조를 인수로 받는다. 직렬화 클래스는 `ValueSerializer` 인터페이스를 구현하여 `Kotlin` 객체에서 해당 `JSON` 표현으로 변환하고, 마찬가지로 `JSON` 값에서 다시 `Kotlin` 객체로 변환해야 한다

```kotlin
interface ValueSerializer<T> {
	fun toJsonValue(value: T): Any?
    fun fromJsonValue(jsonValue: Any?): T
}
```

날짜의 직렬화를 지원해야 하고 이를 위해 `ValueSerializer<Date>` 인터페이스를 구현하는 고유한 `DateSerializer` 클래스를 만들었다고 가정해 보겠다. 

- 이 클래스는 [`JKid` 소스 코드](http://mng.bz/e1vQ)에서 예제로 제공


```kotlin
data class Person(
 	val name: String,
 	@CustomSerializer(DateSerializer::class) val birthDate: Date
)
```

이제 `@CustomSerializer` 어노테이션이 어떻게 선언되는지 살펴보자.  `ValueSerializer` 클래스는 제네릭이며 유형 매개 변수를 정의하므로 유형을 참조 할 때마다 유형 인수 값을 제공해야 한다. 이 어노테이션이 사용될 속성 타입에 대해 아무것도 모르기 때문에 별표 투영을 인수로 사용할 수 있다:

```kotlin
 annotation class CustomSerializer(
 	val serializerClass: KClass<out ValueSerializer<*>>
)
```

어노테이션이 `ValueSerializer` 인터페이스를 구현하는 클래스만 참조할 수 있는지 확인해야 한다. 예를 들어, `Date`는 `ValueSerializer` 인터페이스를 구현하지 않으므로 `@CustomSerializer(Date::class)`를 작성하는것은 금지되어야 한다.

까다로워 보일 수 있지만 좋은 소식은 클래스를 어노테이션 인수로 사용해야 할 때 마다 동일한 패턴을 적용할 수 있다는 것입니다. `KClass<out YourClassName>`을 작성 하고 `YourClassName`에 고유한 유형 인수가 있는 경우 `*`로 대체할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/d10c9700-0983-4be3-b5f4-d2df8950502b/image.png)

## 12.2 리플렉션: 런타임에 Kotlin 객체 인스펙팅하기

간단히 말해, 리플렉션은 해당 속성이 무엇인지 미리 알지 못해도 런타임에 동적으로 객체의 프로퍼티와 메서드에 접근하는 방법이다. 일반적으로 객체의 메서드나 프로퍼티에 접근할 때 프로그램의 소스 코드는 특정 선언을 참조하고 컴파일러는 정적으로 참조를 확인하여 선언이 존재하는지 확인한다. 

그러나 때로는 모든 유형의 객체에서 작동할 수 있거나 액세스하려는 메서드와 프로퍼티의 이름을 런타임에만 알 수 있는 코드를 작성해야 할 때가 있다. 직렬화 라이브러리는 이러한 코드의 좋은 예로, 특정 클래스와 프로퍼티를 참조할 수 없으므로 모든 객체를 `JSON`으로 직렬화할 수 있어야 한다. 여기서 리플렉션이 중요한 역할을 한다.

`Kotlin` 리플렉션 `API`를 사용할 수 있다. 이를 통해 데이터 클래스, 속성 및 `null` 가능 유형과 같은 모든 `Kotlin` 개념에 액세스할 수 있다. 한 가지 중요한 점은 `Kotlin` 리플렉션 `API`는 `Kotlin` 클래스에만 국한되지 않으며, 동일한 API를 사용하여 모든 `JVM`언어로 작성된 클래스에 액세스할 수 있다.

### 12.2.1 Kotlin 리플렉션 API: KClass, KCallable, KFunction 및 KProperty

__`Kotlin` 리플렉션 `API`의 주요 진입점은 클래스를 나타내는 `KClass`이다.__

이를 사용하여 클래스에 포함된 모든 선언과 그 슈퍼클래스 등을 열거하고 액세스할 수 있다. `MyClass::class`를 작성하면 `KClass`의 인스턴스를 얻을 수 있다. 마찬가지로, 런타임에 `myobject` 객체의 클래스를 얻으려면 `myobject::class`를 작성하면 된다:

```kotlin
import kotlin.reflect.full.*
   
class Person(val name: String, val age: Int)

fun main() {
	val person = Person("Alice", 29)
    val kClass = person::class
    println(kClass.simpleName)
    // Person
    kClass.memberProperties.forEach { println(it.name) }
    // age
    // name
}
```

`KClass`의 선언을 살펴보면 클래스의 콘텐츠에 액세스하는 데 유용한 메서드가 많이 포함되어 있다.

```kotlin
interface KClass<T : Any> {
	val simpleName: String?
    val qualifiedName: String?
    val members: Collection<KCallable<*>>
    val constructors: Collection<KFunction<T>>
    val nestedClasses: Collection<KClass<*>>
    // ...
}
```

`KCallable`은 함수와 프로퍼티를 위한 슈퍼 인터페이스이다. 여기에는 호출 메서드를 선언하여 해당 함수나 프로퍼티의 게터를 호출할 수 있다:

```kotlin
interface KCallable<out R> {
    fun call(vararg args: Any?): R
    // ...
}

fun foo(x: Int) = println(x)
fun main() {
	val kFunction = ::foo kFunction.call(42)
	// 42
}
```

`::foo`는 리플렉션 `API`의 `KFunction`클래스 인스턴스이다. 따라서 참조된 함수를 호출하려면 `KCallable.call` 메서드(호출메서드)를 사용해야한다. 

위의 `KFunction`은 `KFunction1<Int, Unit>`으로 변환되며 이는 매개변수의 개수에 따라 함수가 변환된다. 

```kotlin
import kotlin.reflect.KFunction2

fun sum(x: Int, y: Int) = x + y
fun main() {
    val kFunction: KFunction2<Int, Int, Int> = ::sum
    println(kFunction.invoke(1, 2) + kFunction(3, 4))
    // 10
    kFunction(1)
    // ERROR: No value passed for parameter p2
}
```

`KProperty` 인스턴스에서도 호출 메서드를 호출할 수 있으며, 이 메서드는 프로퍼티의 `get`메서드를 호출한다. 그러나 프로퍼티 인터페이스는 속성 값을 가져오는 더 나은 방법인 `get`메서드를 제공한다.

`get` 메서드에 액세스하려면 속성에 맞는 인터페이스를 사용해야 한다. 최상위 읽기 전용 및 변경 가능 프로퍼티는 각각 `KProperty0` 및 `KMutableProperty0` 인터페이스의 인스턴스에 의해 리턴되며, 두 인터페이스 모두 인수가 없는 `get` 메서드를 가지고 있다:

```kotlin
var counter = 0
fun main() {
    val kProperty = ::counter
    kProperty.setter.call(21)
    println(kProperty.get())
    // 21
}
```

```kotlin
class Person(val name: String, val age: Int)

fun main() {
	val person = Person("Alice", 2e) 
	val memberProperty = Person::age println(memberProperty.get(person)) 
    // 2e
}
```

인터페이스(예: KClass, KFunction, KParameter)는 모두
`KAnnotatedElement`를 확장한다. 

- `KClass`는 클래스와 객체를 모두 표현하는데 사용된다. 
- `KProperty`는 모든 프로퍼티를 나타낼 수 있다.
- `KProperty`의 서브클래스인 `KMutableProperty`는 변수로 선언하는 가변 프로퍼티를 나타낸다
   - `Property`와 `KMutableProperty`에 선언된 특수 인터페이스 `Getter`와 `Setter`를 사용하여 프로퍼티 접근자를 함수로 접근할 수 있다. (접근자를 위한 두 인터페이스는 모두 `KFunction`을 확장)
   
간결성을 위해 그림에서 `KClass` `KCallable` `KParameter` `KProperty0`과 같은 프로퍼티에 대한 특정 인터페이스는 생략되었다.

![](https://velog.velcdn.com/images/cksgodl/post/0817e6fd-819a-43a9-bb85-ebfb73dd25a1/image.png)

### 12.2.2 리플렉션을 사용하여 객체 직렬화 구현하기

먼저 JKid의 직렬화 함수 선언을 보자.

```kotlin
fun serialize(obj: Any): String
```

이 함수는 객체를 받아 `JSON` 표현의 문자열로 반환한다. 이 함수는 결과 `JSON`을 `StringBuilder` 인스턴스에 빌드한다. 객체 프로퍼티와 그 값을 직렬화하면서 이 `StringBuilder` 객체에 추가한다. 추가 호출을 더 간결하게 만들기 위해 `StringBuilder`의 확장 함수에 구현을 넣어 보겠다. 

```kotlin
private fun StringBuilder.serializeobject(x: Any) { 
	append(/*...*/)
}
```

```kotlin
fun serialize(obj: Any): String = buildString { serializeobject(obj) }
```

이제 직렬화 함수의 동작에 대해 알아보겠다. 기본적으로 이 함수는 객체의 모든 프로퍼티를 직렬화한다. 원시 유형과 문자열은 적절하게 `JSON` 숫자, 부울 및 문자열 값으로 직렬화한다. 컬렉션은 `JSON` 배열로 직렬화된다. 다른 유형의 프로퍼티는 중첩된 객체로 직렬화된다. 이전 섹션에서 설명했듯이 이 동작은 어노테이션을 통해 사용자 정의할 수 있다.

실제 시나리오에서 리플렉션 API를 관찰할 수 있는 `serializeobject`의 구현을 살 펴보겠다.

```kotlin
private fun StringBuilder.serializeObject(obj: Any) {
    val kClass = obj::class as KClass<Any>
    val properties = kClass.memberProperties
    properties.joinToStringBuilder(
    	this, 
	    prefix = "{", 
    	postfix = "}"
	) { prop ->
		serializeString(prop.name)
		append(": ")
		serializePropertyValue(prop.get(obj))
	}
}
```

`serializePropertyValue` 함수는 값이 기본값, 문자열, 컬렉션 또는 중첩객체인지 확인하여 그 내용을 그에 따라 직렬화한다.

이전 섹션에서는 `KProperty` 인스턴스의 값을 가져오는 방법인 `get` 메서드에 대해 설명다. 컴파일러가 수신자와 속성 값의 정확한 유형을 알 수 있는 `KProperty1<Person, Int>` 타입의 멤버 참조 `Person::age`를 사용했다. 그러나 이 예제에서는 객체 클래스의 모든 프로퍼티를 열거하기 때문에 정확한 유형을 알 수 없다. 

따라서 `prop` 변수의 유형은 `KProperty1<Any, *>`이고, `prop.get(obj)`는 `Any?` 유형의 값을 반환한다. 컴파일 타임에 수신자 유형을 확인하지는 않지만 속 성 목록을 가져온 것과 동일한 객체를 전달하기 때문에 수신자 유형이 정확할 것이다.

### 12.2.3 주석을 사용하여 직렬화 사용자 지정

이 장의 앞부분에서는 `JSON` 직렬화 프로세스를 사용자 정의할 수 있는 어노테이션의 정의를 살펴보았다. 특히 `@JsonExclude`, `@JsonName` 및 `@CustomSerializer` 어노테이션에 대해 설명했다. 이제 이러한 어노테이션이 `serializeobject` 함수에 의해 어떻게 처리되는지 살펴보다.

#### `JsonExclude`

`JsonExclude` 어노테이션을 사용하면 직렬화에서 일부 관계를 제외할 수 있다. 

클래스의 모든 멤버 프로퍼티를 가져오려면 `KClass` 인스턴스에서 확장 프로퍼티 `memberProperties`를 사용한다는 것을 기억하자. 하지만 이제 작업이 더 복잡해졌다. `@JsonExclude`로 주석 처리된 프로퍼티를 필터링해야 한다. 이경우 `findAnnotation` 함수를 사용할 수 있다.

```kotlin
val properties = kClass.memberProperties
        .filter { it.findAnnotation<JsonExclude>() == null }
```

#### `JsonName`
 
```kotlin
annotation class JsonName(val name: String)
data class Person(
    @JsonName("alias") val firstName: String,
    val age: Int
)
```

```kotlin
val jsonNameAnn = prop.findAnnotation<JsonName>()
val propName = jsonNameAnn?.name ?: prop.name
```

`Kclass`의 함수를 활용하여 `annoation`이 존재하면 해당 이름을 사용하고, 이외에는 `prop`의 네임을 사용할 수 있다.

```kotlin
private fun StringBuilder.serializeObject(obj: Any) =
    (obj::class as KClass<Any>)
        .memberProperties
        .filter { it.findAnnotation<JsonExclude>() == null }
        .joinToStringBuilder(this, prefix = "{", postfix = "}")


private fun StringBuilder.serializeProperty(
        prop: KProperty1<Any, *>, obj: Any
){
	val jsonNameAnn = prop.findAnnotation<JsonName>() 
    val propName = jsonNameAnn?.name ?: prop.name serializeString(propName)
	append(": ")
	serializePropertyValue(prop.get(obj))
}
```

> `KClass`란?? 
>
> `KClass`는 코틀린에서 클래스에 대한 런타임 메타데이터를 제공하는 클래스로, 자바의 **Class**와 유사한 역할을 한다. 하지만 자바의 `Class`는 자바 클래스에 대한 정보를 제공하는 반면, 코틀린의 `KClass`는 코틀린의 클래스와 관련된 메타데이터를 제공한다.
```kotlin
val myClass = MyClass::class  // Get KClass for MyClass
```




#### @CustomSerializer

```kotlin
import java.util.Date
data class Person(
    val name: String,
    @CustomSerializer(DateSerializer::class) val birthDate: Date
)
```

```kotlin
fun KProperty<*>.getSerializer(): ValueSerializer<Any?>? {
    val customSerializerAnn = findAnnotation<CustomSerializer>() ?:	return null
    val serializerClass = customSerializerAnn.serializerClass
    val valueSerializer = serializerClass.objectInstance
            ?: serializerClass.createInstance()
    @Suppress("UNCHECKED_CAST")
    return valueSerializer as ValueSerializer<Any?>
}
```

여기서 가장 흥미로운 부분은 클래스와 객체(`Kotlin`의 싱글톤)를 `@CustomSerializer` 어노테이션의 값으로 처리하는 방식이다. 

둘 다 `KClass` 클래스에 의해 표현되지만, 차이점은 객체에는 객체에 대해 생성된 싱글톤 인스턴스에 액세스 하는데 사용할 수 있는 `objectInstance` 속성의 `null`이 아닌 값이 있다는 것이다. 

예를 들어, `DateSerializer`는 객체로 선언되므로 객체의 `objectInstance` 속성은 싱글톤 `DateSerializer` 인스턴스를 저장한다. 이 인스턴스를 사용하여 모든 객체를 직 렬화하면 `createInstance`가 호출되지 않는다. `KClass`가 클래스를 레퍼런싱하는 경우 `createInstance()`를 호출하여 새 인스턴스를 생성한다.

#### 최종 버전

```kotlin
private fun StringBuilder.serializeProperty(
    prop: KProperty1<Any, *>, obj: Any
){
	val jsonNameAnn = prop.findAnnotation<JsonName>() 
    val propName = jsonNameAnn?.name ?: prop.name 
    serializeString(propName)
	append(": ")
	
    val value = prop.get(obj)
	val jsonValue = prop.getSerializer()?.toJsonValue(value) ?: value
	serializePropertyValue(jsonValue) 
}
```

### 12.2.4 JSON 구문 분석 및 객체 역직렬화

역직렬화 함수는 도중에 올바른 결과 객체를 구성할 수 있도록 런타임에 유형 매개변수에 액세스 해야 한다. 앞서 섹션에서 설명했듯이, 이는 유형 매개변수를 리파이너리화해야 함을 의미하며, 함수가 인라인으로 표시되어야 함을 의미한다.

```kotlin
inline fun <reified T: Any> deserialize(json: String): T
```

```kotlin
interface JsonObject {
    fun setSimpleProperty(propertyName: String, value: Any?)
	fun createObject(propertyName: String): JsonObject
    fun createArray(propertyName: String): JsonObject
}
```

이 메서드의 `propertyName` 매개변수는 `JSON`키를 받는다. 따라서 파서 객체가 값으로 포함된 작성자 속성을 발견하면 `createObject("author")` 메서드가 호출된다. 단순값 프로퍼티는 실제 토큰값을 값 인수로 전달하여 `setSimpleProperty`를 호출한다.

`JsonObject`구현은 프로퍼티에 대한 새 객체를 생성하고 외부 객체에 프로퍼티에 대한 참조를 저장하는 역할을 담당한다.

아래 그림은 문자열을 역직렬화할 때 어휘분석과 구문분석의 각 단계의 입력과 출력을 보여준다.
출력으로는 적절한 `JsonObject` 메서드를 호출한다.

![](https://velog.velcdn.com/images/cksgodl/post/2eb33512-40fd-4eed-9728-496bf57bb4f2/image.png)

`JsonObject`는 특정 객체로 매핑되어야 한다. 따라서 아래와 같은 메서드를 호출하여 이를 사용한다.

```kotlin
interface Seed : JsonObject {
    fun spawn(): Any?
    fun createCompositeProperty(
        propertyName: String,
        isList: Boolean
    ): JsonObject {
    
    override fun createObject(propertyName: String) =
        createCompositeProperty(propertyName, false)
    override fun createArray(propertyName: String) =
        createCompositeProperty(propertyName, true)
	// ...
}
```

```kotlin
class ObjectSeed<out T: Any>(
	targetClass: KClass<T>,
    override val classInfoCache: ClassInfoCache
) : Seed {
    
    private val classInfo: ClassInfo<T> =
        classInfoCache[targetClass]
	private val valueArguments = mutableMapOf<KParameter, Any?>() 
	private val seedArguments = mutableMapOf<KParameter, Seed>() 
	private val arguments: Map<KParameter, Any?>
    	get() = valueArguments +
        	    seedArguments.mapValues { it.value.spawn() }

`	override fun setSimpleProperty(propertyName: String, value: Any?) {
   		val param = classInfo.getConstructorParameter(propertyName)
	    valueArguments[param] =
		    classInfo.deserializeConstructorArgument(param, value)
	}
	
	override fun createCompositeProperty(
    	propertyName: String, isList: Boolean
	): Seed {
    	val param = classInfo.getConstructorParameter(propertyName)
    	val deserializeAs =
			classInfo.getDeserializeClass(propertyName)?.starProjectedType
		val seed = createSeedForType(deserializeAs ?: param.type, isList)
		return seed.apply { seedArguments[param] = this }
	}
    
	override fun spawn(): T = classInfo.createInstance(arguments) 
}
```



```kotlin
fun <T: Any> deserialize(json: Reader, targetClass: KClass<T>): T {
    val seed = ObjectSeed(targetClass, ClassInfoCache())
    Parser(json, seed).parse()
    return seed.spawn()
}
```


### 12.2.5 역직렬화의 마지막 단계: callBy() 및 리플렉션을 사용하여 객체 만들기

마지막으로 이해해야 할 부분은 결과 인스턴스를 빌드하고 생성자 매개변수에 대한 정 보를 캐시하는 `ClassInfo` 클래스이다. 세부 사항을 살펴보기 전에 리플렉션을 통해 객체를 생성하는 데 사용하는 `API`를 살펴보자.

```kotlin
interface KCallable<out R> {
    fun callBy(args: Map<KParameter, Any?>): R
    // ...
}
```

이 메서드는 인자로 전달될 해당 값에 대한 매개변수 맵을 받는다. 맵에서 매개변수가 누락된 경우 기본값이 사용된다. 또한 매개변수를 올바른 순서대로 넣을 필요 없이 `JSON`에서 이름-값 쌍을 읽고 각 인수 이름에 해당하는 매개변수를 찾은 다음 그 값을 맵에 넣으면 된다는 추가적인 편의성도 제공한다.

그러나 유형을 올바르게 설정하는 데 주의해야 한다. `args` 맵의 값 유형은 생성자 매개변수 유형과 일치해야 하며, 그렇지 않으면 런타임에 `IllegalArgumentException`이 발생한다. 

이는 숫자 타입의 경우 특히 중요하다. 매개 변수가 `Int`, `Long`, `Double` 등의 다른 기본 유형으로 변환하려면 `JSON`에서 가져온 숫자 값을 올바른 유형으로 변환 해야한다. 이를위해 `KParameter.type` 프로퍼티를 사용한다.

이를 위해 `KType`과 해당 내장 `ValueSerializer` 객체 간의 매핑을 제공하는 작은
함수 `serializerForType`을 제공할 수 있다. `JKid`가 알고 있는 타입(`Byte`, `Int`, `Boolean` 등)의 런타임 표현을 얻으려면 `typeof<>()` 함수를 사용하여 각각의 `KType` 인스턴스를 반환하면 된다.

```kotlin
fun serializerForType(type: KType): ValueSerializer<out Any?>? =
        when (type) {
            typeOf<Byte>() -> ByteSerializer
            typeOf<Int>() -> IntSerializer
            typeOf<Boolean>() -> BooleanSerializer
            // ...
		else -> null
}
```

```kotlin
object BooleanSerializer : ValueSerializer<Boolean> {
    override fun fromJsonValue(jsonValue: Any?): Boolean {
        if (jsonValue !is Boolean) throw JKidException("Boolean expected")
        return jsonValue
    }
    override fun toJsonValue(value: Boolean) = value
}
```

## 요약

- `Kotlin`의 주석은 `@MyAnnotation(params)` 구문을 사용하여 적용.
- `Kotlin`을 사용하면 파일 및 표현식을 비롯한 광범위한 대상에 주석을 적용할 수 있다.
- 어노테이션 인수는 원시값, 문자열, 열거형, 클래스 참조, 다른 어노테이션 클 래스의 인스턴스 또는 그 배열일 수 있다.
- 단일 `Kotlin` 선언이 여러 바이트코드 요소를 생성하는 경우 어노테이션이 적용되는 방식을 선택할 수 있다.
- 어노테이션 클래스를 기본 생성자가 있는 클래스로 선언하면 모든 매개변수가 본문 없이 `val` 프로퍼티로 표시
- `Meta Annotation`을 사용하여 대상, 보존 모드 및 기 타주석의 속성을 지정할 수 있다.
- 리플렉션 `API`를 사용하면 런타임에 객체의 메서드와 프로퍼티를 동적으로 열 거하고 액세스할 수 있다. (여기에는 클래스(KClass), 함수(KFunction) 등과 
같은 다양한 종류의 선언을 나타내는 인터페이스가 있다.)
- `KClass` 인스턴스를 얻으려면 클래스에 `ClassName::class`를 사용하거나 객체 인스턴스에 대한 객체 `이름::클래스`를 사용한다.
- `KFunction`과 `KProperty` 인터페이스는 모두 일반 호출 메서드를 제공하는 `KCallable`을 확장한다.
- `KCallable.callBy` 메서드는 기본 매개변수 값으로 메서드를 호출하는 데 사용할 수 있다.
- `KFunction0, KFunction1` 등은 호출 메서드를 사용하여 호출할 수 있는 매개변수 수가 다른 함수이다.
- `KProperty0`과 `KProperty1`은 값을 검색하기 위한 get 메서드를 지원하는 수신자 수가 다른 프로퍼티이다. 
- `KMutableProperty0`과 `KMutableProperty1`은 이러한 인터페이스를 확장하여 `set` 메서드를 통해 프로퍼티값을 변경할 수 있도록 지원한다.
- `KType`의 런타임 표현을 얻으려면 `typeof<T>()`를 사용하면 된다.


