[KotlinLang-Inline Value Classes](https://kotlinlang.org/docs/inline-classes.html)의 내용과 함께 Value Class에 대한 내용을 설명한다.

## value(Inline) class

개발을 진행하며 값을 클래스에 래핑하여 `도메인 클래스`을 만드는 것이 유용할 수 있다. 

---

> 자바에서는 일급 컬렉션과 같이 도메인 특정 클래스를 만들기도 한다.

```java
// 자바의 일급 콜렉션 
public class PersonList {
    private final List<Person> people;

    public PersonList(List<Person> people) {
        this.people = Collections.unmodifiableList(people);
    }

    public List<Person> getPeople() {
        return people;
    }

    public int getCount() {
        return people.size();
    }

    @Override
    public String toString() {
        return "PersonList{people=" + people + "}";
    }
}
```

코틀린에서 위와 같은 일급 컬렉션을 만들어도 되지만, 이에 대한 자세한 내용은 다음 글을 참고하라. 

- [[Kotlin] 코틀린에서 위임을 통한 일급 콜렉션은 필요 없다.](https://velog.io/@cksgodl/Kotlin-%EC%BD%94%ED%8B%80%EB%A6%B0%EC%97%90%EC%84%9C-%EC%9D%BC%EA%B8%89-%EC%BD%9C%EB%A0%89%EC%85%98%EC%9D%80-%ED%95%84%EC%9A%94-%EC%97%86%EB%8B%A4)  

---

그러나 이와같이 객체(인스턴스)를 생성하는 것은 추가적인 힙 할당으로 인해 런타임 오버헤드를 초래한다. 

`JVM`환경 에서는 일반적으로 원시클래스라고 불리우는 `int`, `long`와 같은 자료형과 다르게 클래스는 참조(`reference`) 타입으로써 힙에 할당되어 특히 성능 저하가 크다. 이런 원시 타입은 일반적으로 런타임에 의해 최적화될 수 있지만, 래퍼런스 타입은 특별한 처리를 받지 않기 때문이다.

이러한 문제를 해결하기 위해, `Kotlin`은 인라인(`value`) 클래스라는 특별한 유형의 클래스를 도입한다. `value` 클래스는 값 기반 클래스이다. 이는 참조를 가지지 않으며 오직 값을 담을 수만 있다. 

> 참조를 가지지 않음으로써 `===` 연산이 불가능 하다.

`value` 클래스를 선언하려면, 클래스 이름 앞에 value 수정자를 사용하면된다:

```kotlin
@JvmInline
value class Password(private val s: String)
```

이런 `value class`를 아직 `backend compiler`에서 완벽하게 지원하지 않음으로 `@JvmInline` 어노테이션을 사용해야 한다.

> `Valhalla`프로젝트를 통해 `JVM`수준에서의 원시타입의 래핑의 컴파일러 최적화를 제공할 예정이지만, 현존 JVM은 이를 지원하지 않는다. 따라서 현재는 값 클래스를 활용하는데 제약이 많다. (@JvmInline을 붙여야 되거나, 파라미터로 값 하나만 등록할 수 있는 등...)


```kotlin
// 클래스 'Password'의 실제 인스턴스화는 일어나지 않습니다
// 런타임에서 'securePassword'는 단지 'String'을 포함합니다
val securePassword = Password("Don't try this in production")
```

결과로 런타임에서는 인라인 클래스의 인스턴스를 생성하지 않고 원시타입으로 표현되게 될 수 있다.

`value` 클래스의 주요 특징이 이것이다. 이름에서 알 수 있듯이, 인라인 클래스는 데이터가 사용되는 곳에 인라인되어 표현된다. (이는 인라인 함수의 내용이 호출 지점에 인라인되는 것과 유사)

### value class Example

이를 활용해 **"도메인 특정 유형을 만드는 것"**의 예제는 다음과 같다. 

```kotlin
@JvmInline
value class Centimeter(val value: Double) {
    init {
        require(value >= 0) { "Length must be non-negative" }
    }

    fun toMillimeters() = Millimeter(value * 10)
}

@JvmInline
value class Millimeter(val value: Double) {
    init {
        require(value >= 0) { "Length must be non-negative" }
    }

    fun toCentimeters() = Centimeter(value / 10)
}

fun main() {
    val lengthInCm = Centimeter(25.0)
    val lengthInMm = lengthInCm.toMillimeters()
    
    println("Length in centimeters: ${lengthInCm.value} cm")
    println("Length in millimeters: ${lengthInMm.value} mm")

    val anotherLengthInMm = Millimeter(150.0)
    val convertedBackToCm = anotherLengthInMm.toCentimeters()

    println("Another length in millimeters: ${anotherLengthInMm.value} mm")
    println("Converted back to centimeters: ${convertedBackToCm.value} cm")
}
```

위와 같이 단위를 표현하는 클래스의 경우 기존에는 Sealed Class를 활용하여 구현할 수 있겠지만, `value class`를 활용하면 더 가독성있고 호율적으로 표현 가능하다. 또한 `toMillimeters()` 등의 메서드를 사용하여 센티미터를 밀리미터로 변환할 수 있다.

> `value class`를 사용하여 센티미터와 밀리미터를 캡슐화할 수 있으며, 단위의 의미를 명확히 하고, 계산 및 변환을 안전하게 수행할 수 있다.


## 멤버변수

인라인 클래스는 일반 클래스의 일부 기능도 지원한다. 특히, 인라인 클래스는 프로퍼티와 함수를 선언할 수 있으며, 초기화 블록(`init block`)과 보조 생성자(`secondary constructor`)를 가질 수 있다:

```kotlin
@JvmInline
value class Person(private val fullName: String) {
    init {
        require(fullName.isNotEmpty()) {
            "Full name shouldn't be empty"
        }
    }
  
    constructor(firstName: String, lastName: String) : this("$firstName $lastName") {
        require(lastName.isNotBlank()) {
            "Last name shouldn't be empty"
        }
    }
  
    val length: Int
        get() = fullName.length
  
    fun greet() {
        println("Hello, $fullName")
    }
}
  
fun main() {
    val name1 = Person("Kotlin", "Mascot")
    val name2 = Person("Kodee")
    name1.greet() // `greet()` 함수는 정적 메서드로 호출됩니다
    println(name2.length) // 속성 getter는 정적 메서드로 호출됩니다
}
```

인라인 클래스의 속성은 백킹 필드를 가질 수 없다. 

> `backing field`는 프로퍼티의 값을 저장하기 위한 필드이다. 코틀린의 프로퍼티 생성시 자동으로 backing field가 생기며, 아래와 같이 커스텀하게 작성할 수도 있다.

```kotlin
var counter = 0 
        set(value) {
            if (value >= 0) field = value
        }
}
```

인라인 클래스는 단순히 계산이 가능한 프로퍼티만 가질 수 있으며 (`lateinit` 또는 `delegated` 속성은 사용할 수 없음) `greet()` 함수와 `length` 속성은 정적 메서드처럼 호출된다. 정적 메서드 처럼 호출되는 과정은 아래의 이후 나올 내용인 `맹글링`을 참고하라. 

## 상속 지원

value 클래스는 인터페이스 상속을 지원한다:

```kotlin
interface Printable {
    fun prettyPrint(): String
}

@JvmInline
value class Name(val s: String) : Printable {
    override fun prettyPrint(): String = "Let's $s!"
}

fun main() {
    val name = Name("Kotlin")
    println(name.prettyPrint()) // 정적 메소드로 실행
}
```

 인라인 클래스는 다른 클래스를 확장할 수 없으며(인라인 클래스를 또 다른 클래스가 상속받을 수는 없음) 항상 final이다.
 
## 박싱과 참조에 대해

컴파일러에 의해 생성된 바이트 코드에서, `Kotlin` 컴파일러는 각 인라인 클래스에 대해 박싱된 상태를 유지할 수도 있다. 

> 즉, 인라인 클래스의 인스턴스는 런타임에서 래퍼 또는 기본 타입으로 두개 다로 표현될 수 있다. 

이는 `Int`가 원시 `int`로 표현될 수도 있고 래퍼 `Integer`로 표현될 수도 있는 것과 동일하다.

`Kotlin` 컴파일러는 최적화된 성능의 코드를 생성하기 위해 기본 타입을 사용하는 것을 선호한다. 그러나 때때로 래퍼(참조)를 유지해야 하는 경우가 있다.

아래 예제를 보자.

```kotlin
interface I

@JvmInline
value class Foo(val i: Int) : I

fun asInline(f: Foo) {}
fun <T> asGeneric(x: T) {}
fun asInterface(i: I) {}
fun asNullable(i: Foo?) {}

fun <T> id(x: T): T = x

fun main() {
    val f = Foo(42)

    asInline(f)    // 언박스됨: Foo 자체로 사용됨
    asGeneric(f)   // 박싱됨: 제너릭 타입 T로 사용됨
    asInterface(f) // 박싱됨: 타입 I로 사용됨
    asNullable(f)  // 박싱됨: Foo?로 사용됨 (Foo와는 다름)

    // 아래에서 'f'는 'id'에 전달되면서 먼저 박싱되고, 'id'에서 반환되면서 다시 언박싱됩니다.
    // 최종적으로, 'c'는 언박스된 표현(단순히 '42')을 포함하게 됩니다.
    val c = id(f)
}
```

위와같이

- 제너릭
- `nullable`타입
- 상위 타입

일 때는 인라인 클래스도 래퍼(참조)의 형태가 될 수 있다. 하지만 원시타입과 참조타입이 공존함으로 참조 동등성은 무의미하며 따라서 `===` 연산은 금지된다.

인라인 클래스는 또한 기본 타입으로 제너릭 타입 매개변수를 가질 수 있다. 이 경우, 컴파일러는 이를 `Any?` 또는 일반적으로 타입 매개변수의 부모타입으로 매핑한다. (이 떄는 박싱되어 사용되며 인라인 클래스를 사용하는 장점이 없어진다.)

> `Int`, `Long`, `Double`과 같은 코틀린 클래스또한 `Class`로 구현이 된다.
> 
> ![](https://velog.velcdn.com/images/cksgodl/post/a3a321f7-b079-419a-995f-c2678dfe5b6b/image.png)
>
> 따라서 이는 컴파일러에 의해 `int`와 같은 원시 클래스로 바뀌어 실행된다. 


참고) 원시 타입인 `Int`형끼리의 `===`연산은 수행은 권장되지 않는다.

하지만, `Int` -> `Any`로 래핑될 경우 `===`연산 수행이 가능해지며, 이때 기존타입과의 연산은 실패하게 된다. 이는 인라인 클래스일 때도 동일하다.

```kotlin
fun main() {
    val a = 2021
    val b = a
    val aRef: Any = a // coerce a value to Any
    val bRef: Any = b // coerce b value to Any
    println(aRef == bRef) // true -- same value
    println(aRef === bRef) // false -- different instance
}
```

## 맹글링(Mangling)

인라인 클래스는 클래스를 함수 내부로 옮겨 컴파일하기 때문에 다양한 오류가 발생할 수 있다. 예를 들어, 예상치 못한 네이밍 충돌이 발생할 수 있다:

```kotlin
@JvmInline
value class UInt(val x: Int)

// 바이트코드에서 'public final void compute(int x)'로 표현됨
fun compute(x: Int) { }

// 바이트코드에서 'public final void compute(int x)'로 표현됨!
fun compute(x: UInt) { }
```

이러한 문제를 완화하기 위해, 인라인 클래스를 사용하는 함수는 함수 이름에 안정적인 해시코드를 추가하여 이름을 변형한다. 따라서 `fun compute(x: UInt)`는 `public final void compute-<hashcode>(int x)`로 표현되어 충돌 문제가 해결된다. 이를 맹글링이라고 한다.

아래의 예제에서 더 자세히 알아본다.

### 임의로 맹글링 방지하기

`Java` 코드에서 인라인 클래스를 받는 함수의 네이밍을 직접 지정할 수 있다. `@JvmName` 어노테이션을 활용하면 된다:

```kotlin
@JvmInline
value class UInt(val x: Int)

fun compute(x: Int) { }

@JvmName("computeUInt")
fun compute(x: UInt) { }
```

## Inline classes vs type aliases

인라인 클래스와 `type aliases`가  유사해 보일 수 있다. 실제로, 두 가지 모두 새로운 타입을 도입하며, 런타임에서 기본 타입으로 표현된다.

그러나 결정적인 차이점은 `type aliases`는 기본 타입과(또는 상위 타입)과 할당 호환이 되는 반면(타입 불안전), 인라인 클래스는 그렇지 않다. 

> 무공변성과 동일하게 인라인 클래스만 할당될 수 있도록 컴파일 단계에서 검증한다.


```kotlin
typealias NameTypeAlias = String

@JvmInline
value class NameInlineClass(val s: String)

fun acceptString(s: String) {}
fun acceptNameTypeAlias(n: NameTypeAlias) {}
fun acceptNameInlineClass(p: NameInlineClass) {}

fun main() {
    val nameAlias: NameTypeAlias = ""
    val nameInlineClass: NameInlineClass = NameInlineClass("")
    val string: String = ""

    acceptString(nameAlias) // OK: 별칭을 기본 타입 대신 전달 가능
    acceptString(nameInlineClass) // Not OK: 인라인 클래스를 기본 타입 대신 전달할 수 없음

    acceptNameTypeAlias(string) // OK: 기본 타입을 별칭 대신 전달 가능
    acceptNameInlineClass(string) // Not OK: 기본 타입을 인라인 클래스 대신 전달할 수 없음
}
```


## 인라인 클래스와 위임

인라인 클래스의 인라인 값에 대한 위임을 사용하여 인터페이스를 구현하는 것은 허용된다:

```kotlin
코드 복사
interface MyInterface {
    fun bar()
    fun foo() = "foo"
}

@JvmInline
value class MyInterfaceWrapper(val myInterface: MyInterface) : MyInterface by myInterface

fun main() {
    val my = MyInterfaceWrapper(object : MyInterface {
        override fun bar() {
            // 본문
        }
    })
    println(my.foo()) // "foo"를 출력
}
```

이 예제에서 `MyInterfaceWrapper` 클래스는 `MyInterface`를 구현하고, `myInterface`를 사용하여 인터페이스의 구현을 위임한다. `MyInterfaceWrapper` 인스턴스에서 `foo()`를 호출하면, `MyInterface` 인터페이스의 기본 구현인 `"foo"`가 출력된다.

> 하지만 부모(상위) 타입을 활용하는 함수에서는 이는 박싱되어 사용될 수 있다.

## 실 동작 예시

- 전체 소스

```kotlin
data class DataPerson(
    private val fullName: String
)

@JvmInline
value class Person(private val fullName: String) {

    init {
        if (fullName.isEmpty()) throw Error()
    }

    constructor(firstName: String, secondName: String) : this(firstName + secondName)

    fun greet() = "Hello! I'm $fullName"

    companion object {

        fun of(name: String) = Person(name)
    }
}

class ValueClassTest {

    fun someFunction(person: Person) {
        println("someFunction $person")
    }

    fun someFunction(person: String) {
        println("someFunction $person")
    }

    @Test
    fun getValueClass() {
        val person1 = Person("Person1")
        println(person1.greet())
        val person2 = Person("")
        println(person2.greet())
        val person3 = Person.of("Person3")
        println(person3.greet())

        println(person2 == person1)
        DataPerson("Person4")
    }
}
```

위의 예시를 기반으로 value class가 실제 동작하는 예시를 알아보자.

### `Static`을 통한 인스턴스 생성 방지

```java
   @Test
   public final void testValueClass() {
      String person1 = Person.constructor-impl("Person1");
      String person2 = Person.greet-impl(person1);
      System.out.println(person2);
      person2 = Person.constructor-impl("");
      String person3 = Person.greet-impl(person2);
      System.out.println(person3);
      person3 = Person.Companion.of-ZMX6tQA("Person3");
      String var4 = Person.greet-impl(person3);
      System.out.println(var4);
      // ...
   }
```

위에 소스와 같이 인라인을 통해 `Person`생성자가 `Person.constructor-impl`을 호출하고 `String`을 반환하도록 변경되었다.

중요한 것은 `constructor-impl`에서 타입에 대한 체크 및 검증을 수행한다는 것이다.

```kotlin
   @NotNull
   public static String constructor_impl(@NotNull String fullName) {
      Intrinsics.checkNotNullParameter(fullName, "fullName");
      CharSequence var1 = (CharSequence)fullName;
      // init 블럭에 사용한 검증 진행
      if (var1.length() == 0) {
         throw (Throwable)(new Error());
      } else {
         return fullName;
      }
   }
```

이 외에도

- `companion obejct`로 생성한 확장 팩토리 함수또한 맹글링이 되어 함수를 호출하는 것을 확인할 수 있다. (`Person.Companion.of-ZMX6tQA`)
- `Person`의 멤버함수 들도 `Static`으로 치환되게 되며 인자로 `String`을 받는 형식으로 전환된다.
```kotlin
   @NotNull
   public static final String greet_impl(String $this) {
      return "Hello! I'm " + $this;
   }
```

### `Person`활용 함수 맹글링

```java
   public final void someFunction_A6g30Jw(@NotNull String person) {
      Intrinsics.checkNotNullParameter(person, "person");
      String var2 = "someFunction " + Person.toString-impl(person);
      System.out.println(var2);
   }

   public final void someFunction(@NotNull String person) {
      Intrinsics.checkNotNullParameter(person, "person");
      String var2 = "someFunction " + person;
      System.out.println(var2);
   }
```

`person`이 컴파일 시 `String`으로 치환되면서, `someFunction`네이밍이 겹치기에 이에따라 맹글링을 통해 새로운 함수를 만들어 낸다. 

> 이에 따라 바이트코드의 크기는 증가할 수 있으나 이는 미미하고, 런타임에 객체를 생성하는 비용보다 적어 효율적이다.

### toString, hashCode, equals 함수 구현

```java
   public static String toString_impl(String var0) {
      return "Person(fullName=" + var0 + ")";
   }

   public static int hashCode_impl(String var0) {
      return var0 != null ? var0.hashCode() : 0;
   }

   public static boolean equals_impl(String var0, Object var1) {
      if (var1 instanceof Person) {
         String var2 = ((Person)var1).unbox-impl();
         if (Intrinsics.areEqual(var0, var2)) {
            return true;
         }
      }

      return false;
   }
```

구현되는 함수 또한 String을 활용하도록 다음과 같이 변경되어 사용된다.


## Data Classes vs Value Classes

- 데이터를 저장하는 클래스: Data Class
- 값을 저장하는 클래스 : Value Class

사용하는 목적이 다름으로 동작방식또한 다른 것이 몇 가지 있다.

#### 생성하는 메소드

- `Data Class` : `equals(), toString(), hashCode(), copy(),
componentN()`
- `Value class` : `equals(), toString(), hashCode()`
    
#### `===` 연산의 방지 금지

`value class`는 인스턴스를 생성하지 않음으로 `==` 연산만 지원하고
`===` 연산은 지원하지 않는다.

#### 반드시 val 프로퍼티만 허용

`value class`는 반드시 `Immutable`하다. 이는 `var`이 될 경우 이를 참조할 인스턴스가 존재하는 것과 동일하게 되기에 이를 금지한다.

- 참조 및 식별에 대한 자세한 내용은 [value class 디자인 노트](https://github.com/Kotlin/KEEP/blob/master/notes/value-classes.md)를 참고하라.

```kotlin
value class Box(var mutableProperty) // Value class primary constructor must have only final read-only (val) property parameter
```

#### 하나의 프로퍼티만 가능하다.

현재는 `value class`에 프로퍼티를 하나만 정의 가능하다. 발할라 JVM이 업데이트됨에 따라 여러 프로퍼티가 지원될 예정이다.

