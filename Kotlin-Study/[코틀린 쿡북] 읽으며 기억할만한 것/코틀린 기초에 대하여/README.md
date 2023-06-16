# 코틀린 기초

## 목차

[스마트 캐스트](##스마트-캐스트)

[JvmOverLoad](##JvmOverLoad)

[명시적으로 타입변환하기](##명시적으로-타입변환하기)

[이진법 변환](##이진법-변환)

[숫자 거듭제곱하기](##숫자-거듭제곱하기)

[코틀린에서의 비트 연산](##코틀린에서의-비트-연산)

## 스마트 캐스트

```kotlin
data class Person(
    val firstName: String?,
    val lastName: String,
)

val person = Person(
    firstName = "Hello",
    lastName = "Nice"
)
```

다음과 같은 `Person` 클래스가 있을 때

```kotlin
if (person.firstName != null) {
	// 스마트 캐스트 지원, Null체크 없이 해당 변수 사용 가능
    println(person.firstName.length)
} else {
    println("FirstName Is Null")
}
```

다음과 같이 `null`이 아님을 한번 체크하면 해당 변수를 `null`체크 없이 활용할 수 있습니다.

이를 자바로 디컴파일해보면 다음과 같이 출력됩니다.

```java
   public static final void main() {
      Person person = new Person("Hello", "Nice");
      if (person.getFirstName() != null) {
         String var10000 = person.getFirstName();
         Intrinsics.checkNotNull(var10000); // Null이 아님를 체크 함
         int var1 = var10000.length(); // Int형으로 Length사용
         System.out.println(var1);
      } else {
         String var2 = "FirstName Is Null";
         System.out.println(var2);
      }
   }
```

모든 상황에서 이처럼 스마트 캐스트를 지원하는 것은 아닙니다.

`firstName`가 `var`로 설정되어있다면 `null`체크를 한번 진행하더라도 값이 변경될 수 있기에 스마트 캐스트를 지원하지 않습니다.

```kotlin
data class Person(
    var firstName: String?,
    val lastName: String,
)

if (person.firstName != null) {
	// Smart cast to 'String' is impossible,
    // because 'person.firstName' is a mutable property that could have been changed by this time
    println(person.firstName?.length) // 널체크를 또 진행해야함
} else {
    println("FirstName Is Null")
}
```

해당 소스를 자바로 디컴파일하면 다음과 같습니다.

```kotlin
   public static final void main() {
      Person person = new Person("Hello", "Nice");
      if (person.getFirstName() != null) {
         String var10000 = person.getFirstName();
         // Null체크를 따로 진행하지 않고, safeCall에 따른 null을 그냥 반환 함
         Integer var1 = var10000 != null ? var10000.length() : null;
         System.out.println(var1);
      } else {
         String var2 = "FirstName Is Null";
         System.out.println(var2);
      }
   }
```

### 요약

> 스마트 캐스트를 지원받기 위해서는 `val`로 변수를 지정해야 합니다.

또한 `as?`식을 지원하여 타입캐스트를 실패했을 때 null을 반환하도록 소스를 작성할 수도 있습니다.

```kotlin
val p1 = person as? Person ?:
	throw IllegalStateException("타입 변환 실패")
```

---

## JvmOverLoad

```kotlin
fun addProduct(name: String, price: Double = 0.0, desc: String? = null) =
    "Adding product with $name, ${desc ?: "NONE"}, and $price"
```

위의 함수는 `name`을 제외한 파라미터는 모두 기본파라미터를 제공하고 있습니다.

코틀린에서 위의 함수의 실행은 제한이 없지만 자바에서의 해당 함수를 활용하기 위해서는 모든 인자를 추가해줘야 합니다.

```kotlin
// Kotlin
println(addProduct("Test1")) // OK
println(addProduct("Test2", 200.0)) // OK
println(addProduct("Test3", 300.0, "ASC")) // OK

// Java
System.out.println(addProduct("Test1")) // Error!!
System.out.println(addProduct("Test3", 300.0, "ASC")) // OK
```

이를 방지하기 위해서 코틀린에서는 `JvmOverload`어노테이션을 제공합니다. 해당 어노테이션을 활용하면 모든 함수를 구현해줍니다.

```kotlin
@JvmOverloads
fun addProduct(name: String, price: Double = 0.0, desc: String? = null) =
    "Adding product with $name, ${desc ?: "NONE"}, and $price"

// Java
System.out.println(addProduct("Test1")) // Ok!!
```

이것이 동작하는 원리는 `Java`로 디컴파일하면 알 수 있습니다.

```java

    // JvmOverLoad X
	@NotNull
   public static final String addProduct(@NotNull String name, double price, @Nullable String desc) {
      Intrinsics.checkNotNullParameter(name, "name");
      StringBuilder var10000 = (new StringBuilder()).append("Adding product with ").append(name).append(", ");
      String var10001 = desc;
      if (desc == null) {
         var10001 = "NONE";
      }

      return var10000.append(var10001).append(", and ").append(price).toString();
   }

   // JvmOverLoad O
   @JvmOverloads
   @NotNull
   public static final String addProduct(@NotNull String name, double price, @Nullable String desc) {
      // ...
      return var10000.append(var10001).append(", and ").append(price).toString();
   }

   @JvmOverloads
   @NotNull
   public static final String addProduct(@NotNull String name, double price) {
      return addProduct$default(name, price, (String)null, 4, (Object)null);
   }

   @JvmOverloads
   @NotNull
   public static final String addProduct(@NotNull String name) {
      return addProduct$default(name, 0.0, (String)null, 6, (Object)null);
   }
```

`JvmOverloads`는 모든 함수를 오버로드하여 구현해주고 있음을 알 수 있습니다.

이는 함수뿐만 아니라 클래스의 생성자에도 똑같이 적용됩니다.

```kotlin
// 생성자에 사용할 땐 constructor를 꼭 명시해주기!
data class Person @JvmOverloads constructor(
	val name: String,
    val price: Double = 0.0,
    val desc: String? = null
)
```

### 요약

디폴트 아규먼트를 JVM 환경에서 제공하고자 한다면 `@JvmOverLoads`어노테이션을 활용하세요.

---

## 명시적으로 타입변환하기

`Int` < `Long`인 것은 개발자로써는 당연하게 이해가 될 것이지만,
하지만 코틀린에서 다음과 같은 식은 제공하지 않습니다.

```kotlin
var a : Int = 5
var b : Long = 4

b = a // Type mismatch -> Required: Long, Found: Int
```

따라서 명시적으로 타입변환을 해주어야 합니다.

```kotlin
b = a.toLong()

// Java Decompile
public static final void main() {
      int a = 5;
      long b = 4L;
      b = (long)a;
}
```

하지만 연산을 수행할 때는 명시적 타입 변환이 필요하지 않습니다!

```kotlin
b = a + 5L

public static final void main() {
      int a = 5;
      long b = 4L;
      b = (long)a + 5L;
}
```

---

## 이진법 변환

> 이 세상에는, 10종류의 사람이 있습니다.
> 이진법을 아는 사람, 이진법을 모르는 사람,
> 그리고 이 농담이 실제로 3진(ternary)농담인지 모르는 사람

```kotlin
val joke = """
이 세상에는, ${3.toString(3)}종류의 사람이 있습니다.
이진법을 아는 사람, 이진법을 모르는 사람,
그리고 이 농담이 실제로 3진(ternary)농담인지 모르는 사람
"""
println(joke)
```

`toString(N진수)`를 활용해 간단하게 진수 변환을 할 수 있습니다.

---

## 숫자 거듭제곱하기

코틀린에서는 거듭제곱 연산자를 제공하지 않습니다. 따라서 코딩테스트를 풀때, 자바에서의 `java.lang.Math`내부의

```java
public static double Math.pow(double a, double b)
```

를 활용하여 거듭제곱을 구현하곤 했습니다.

하지만 `Kotlin`의 `int`형은 `double`형으로 자동 승격되지 않고, 이를 활용하기 위해서는 형변환을 여러번 거쳐야되는 정말 끔찍한 경험을 해야합니다.

```kotlin
val a = 3
println(Math.pow(a.toDouble(), a.toDouble()).toInt())
```

이러한 복잡한 과정을`Int에 대한 확장함수` 및 `infix` 어노테이션을 활용해 간단하게 구현할 수 있습니다.

```kotlin
infix fun Int.`**`(x: Int) = this.toDouble().pow(x).toInt()
fun Int.pow(x: Int) = this `**` x

val a = 3
println(a `**` 3)
```

``**` ` 과 같이 따음표가 맘에 안든다면 다른 이름을 활용하는 방법밖에 없습니다.

---

## 코틀린에서의 비트 연산

### 시프트 연산

코틀린에서의 비트연산을 제공하기 위해 몇가지 함수가 정의되어 있습니다.

- `shl` : 부호가 있는 왼쪽 시프트
- `shr` : 부호가 있는 오른쪽 시프트
- `ushr` : 부호가 없는 오른쪽 시프트 연산

해당 연산들은 `Int`, `Long`타입에만 정의되어 있습니다!

```kotlin
public infix fun shl(bitCount: Int): Int
public infix fun shl(bitCount: Int): Long
```

실제 활용예는 다음과 같습니다.

```kotlin
println(1 shl 1) // 2 -> 0000_0010
println(1 shl 2) // 4 -> 0000_0100
println(1 shl 3) // 8 -> 0000_1000

println(8 shr 1) // 4 -> 0000_0100
```

`ushr`은 부호를 생각하지 않고 연산을 진행하기에 다음과 같은 값이 나오게 됩니다.

```kotlin
val n = -5

println(n shr 1) // -3
println(n ushr 1) // 2_145_483_645
// 7fff_fffd
// 0111_1111_1111_1111_1111_1111_1111_1011
```

이를 활용하여 큰 정수 2개에서의 중간 값을 찾는 알고리즘에 활용할 수 있습니다.

```kotlin
val high = (0.99 * Int.MAX_VALUE).toInt()
val low = (0.75 * Int.MAX_VALUE).toInt()

val mid1 = (high+low) / 2
val mid2 = (high+low) ushr 1 // 두 수의 합은 Int보다 크기에 음수입니다.

println(mid1 !in low..high) // true
println(mid2 in low..high) // true
```

### 비트 불리언 연산

코틀린에서는 `and`, `or`, `xor`, `inv`비트 연산자를 제공합니다.

해당 연산또한 `int`, `long`형에서 제공하고 있습니다.

```kotlin
public infix fun and(other: Int): Int
public infix fun and(other: Long): Long
```

실제 사용 예는 다음과 같습니다.

```kotlin
val n1 = 0b0000_1100 // 십진수 12
val n2 = 0b0001_1001 // 십진수 25

println(n1 and n2) // 8 -> 0000_10000
println(n1 or n2) // 29 -> 0001_1101
println(n1 xor n2) // 21 -> 0001_0101
println(n1.inv()) // invert -> 25의 1의 보수 -13
```

`0b`는 이진수를 의미합니다.

---
