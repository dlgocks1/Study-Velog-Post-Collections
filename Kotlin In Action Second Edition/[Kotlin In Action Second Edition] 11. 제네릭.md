## 11.1 형 인자를 사용하여 형 생성하기: 일반 타입 매개변수

```kotlin
val authors = listof("Sveta", "Seb", "Dima", "Roman")
```

`listof` 함수에 전달되는 모든 값은 문자열이므로 컴파일러는 사용자가`List<String>`을 생성한다고 추론한다.

![](https://velog.velcdn.com/images/cksgodl/post/0f2badda-5a79-4ddf-8f4f-dbaeb786ecf8/image.png)

반면에 빈 목록을 만들어야 하는 경우 유형 인수를 유추할 수 있는 것이 없으므로 명시적으로 지정해야 한다. 

```kotlin
val readers: MutableList<String> = mutableListof()
val readers = mutableListof<String>()
```

> `Kotlin`에는 원시 유형이 없다.
`Java`와 달리 `Kotlin`에서는 항상 유형 인수를 명시적으로 지정하거나 컴파일러에서 유추해야 한다. 
>
> 제네릭은 Java 버전 1.5에만 추가되었기 때문에 이전 버전용으로 작성된 코드와의 호환성을 유지해야 했으므로 유형 인수가 없는 제네릭 유형(소위 원시 유형)을 사용할 수 있다. 예를 들어, `Java`에서는 어떤 종류의 항목이 포함되는지 지정하지 않고 `ArrayList` 유형의 변수를 선언할 수 있다
>
> `Kotlin`은 처음부터 제네릭을 사용했기 때문에 원시 유형을 지원하지 않으며, 유형 인수는 항상 정의해야 한다. 프로그램에서 `Java` 코드에서 원시 유형의 변수를 받는 경우 7.12절에 서 살펴본 대로 플랫폼 유형인 Any!으로 치환된다.

### 11.1.1 일반유형과 함께 작동하는 함수 및 속성

![](https://velog.velcdn.com/images/cksgodl/post/3af5dfe7-2d01-41ef-a342-eb651fac8cfe/image.png)

```kotlin
fun main() {
    val authors = listOf("Sveta", "Seb", "Roman", "Dima")
    val readers = mutableListOf<String>("Seb", "Hadi")
    println(readers.filter { it !in authors })
    // [Hadi]
}
```

일반유형의 제네릭은 모두 컴파일러가 추론해서 작동하며, 컴파일러가 인지하지못하면 컴파일 에러가 발생한다.

### 11.1.2 제너릭 클래스는 꺾쇠 괄호 구문으로 선언

```kotlin
interface List<T> {
    operator fun get(index: Int): T
    // ...
}


interface Comparable<T> {
    fun compareTo(other: T): Int
}
class String : Comparable<String> {
    override fun compareTo(other: String): Int = TODO()
}
```

### 11.1.3 제너릭 클래스 또는 함수가 사용할 수 있는 타입을 제한

타입 매개변수 제약 조건을 사용하면 클래스나 함수의 타입 인수로 사용할 수 있는 타입을 제한할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/9382f58c-6f29-482b-97a8-71d678846cad/image.png)

```kotlin
fun <T: Comparable<T>> max(first: T, second: T): T {
    return if (first > second) first else second
}

fun main() {
    println(max("kotlin", "java"))
    // kotlin
}
```

드물지만 유형 매개변수에 여러 제약 조건을 지정해야 하는 경우에는 약간 다른 구문을 사용할 수 있다.

```kotlin 
fun <T> ensureTrailingPeriod(seq: T)
        where T : CharSequence, T : Appendable 
```

### 11.1.4 유형 매개 변수 non-nullable 명시적으로 표시

제네릭 클래스나 함수를 선언하는 경우, 널가능 인수를 포함한 모든 타입인수를 해당 타입 매개변수를 사용할 수 있다.

```kotlin
class Processor<T> {
    fun process(value: T) {
        value?.hashCode()
    }
}
```

하지만 위와 같이 널체크가 필요하므로 아래와 같이 사용하면 non-nullable로 명시적으로 표시할수 있다.

```kotlin
// 기본값인 Any? 대신 Any를 상한으로 사용
class Processor<T : Any> {
    fun process(value: T) {
        value.hashCode()
	}
}
```

## 11.2 런타임에 제네릭: 유형 매개변수 지우기 및 재정의

구현 관점에서 볼 때 `Java` 가상 머신(`JVM`)의 제네릭은  유형 지우기를 통해 구현된다. 즉, 제네릭 클래스 인스턴스의 유형 인수가 런타임에 보존되지 않는다.

이 섹션에서는 유형 삭제가 `Kotlin`에 미치는 실질적인 영향과 함수를 인라인으로 선언하여 유형 삭제의 한계를 극복하는 방법에 대해 설명한다. 

### 11.2.1 런타임에 제네릭 클래스의 유형 정보를 찾는 데 제한이 있다

`Kotlin`의 제네릭은 런타임에 지워진다. 즉, 제네릭 클래스의 인스턴스에는 해당 인스턴스를 만드는 데 사용된 유형 인수에 대한 정보가 포함되지 않는다.

```kotlin
val list1: List<String> = listOf("a", "b")
val list2: List<Int> = listOf(1, 2, 3)
```

컴파일러는 리스트에 대해 두 가지 다른 유형을 보지만 실행 시에는 완전히 동일하게 표시된다. 

![](https://velog.velcdn.com/images/cksgodl/post/63e606f4-fc09-4245-b06d-1cae581cb340/image.png)

- 런타임에 list1과 list2가 문자열 목록으로 선언되었는지 정수 리스트으로 선언되었는지 알 수 없다.

따라서 `is` 검사를 통해 숫자와 문자열 리스트을 구분하려고 하면 컴파일되지 않는다.

```kotlin
fun printList(l: List<Any>) {
    when(l) {
        is List<String> -> println("Strings: $l")
        is List<Int> -> println("Integers: $l")
	}
}

// Error:Cannotcheckforan instanceoferasedtype
```

제네릭 타입 정보를 지우면 메모리에 저장해야 하는 타입 정보가 줄어들기 때문에 애플 리케이션에서 사용하는 전체 메모리 양이 줄어든다는 장점이 있다.

앞서 설명했듯이 `Kotlin`에서는 유형 인수를 지정하지 않고 일반 유형을 사용할 수 없다. 따라서 값이 집합이나 다른 객체가 아닌 리스트인지 확인하는 방법이 궁금할 수 있다. 

코틀린에서는 특별한 별표 투영 구문을 사용하여 확인할 수 있다:

```kotlin
if (value is List<*>) { /* ... */ }
```

타입에 있는 모든 타입매개변수에 대해 `*`(projection)를 포함해야 한다. 이는 지금은 알 수없는 인자가 있는 타입(또는 Java의 `List<?>`와 유사)을 전달한다고 생각하면 된다.

```kotlin
fun printSum(c: Collection<*>) {
    val intList = c as? List<Int>
        ?: throw IllegalArgumentException("List is expected")
    println(intList.sum())
}
```

컴파일러는 경고만 발생하므로 이 코드는 정상적으로 컴파일된다.

위예제는 정상 컴파일이 진행되며 런타임시에 `ClassCastException`이 발생하게 된다.

### 11.2.2 `reified`된 유형 매개변수가 있는 함수는 런타임에 실제 유형 인수를 참조할 수 있다.

앞서 설명한 것처럼 Kotlin 제네릭은 런타임에 지워지므로 제네릭 클래스의 인스턴스가 있는 경우 인스턴스가 생성될 때 사용된 유형 인수를 찾을 수 없다. 

```kotlin
   fun <T> isA(value: Any) = value is T
        // Error: Cannot check for instance of erased type: T
```

인라인 함수를 사용하면 이를 회피할 수 있다. 인라인 함수의 타입 매개변수를 재정의할 수 있으므로 런타임에 실제 타입 인수를 참조할 수 있다.

```kotlin
inline fun <reified T> isA(value: Any) = value is T

fun main() {
    println(isA<String>("abc"))
    // true
    println(isA<String>(123))
    // false
}
```

`filterIsInstance`또한 위처럼 인라인함수를 활용해 구현된다.

```kotlin
fun main() {
	val items = listof("one", 2, "three") 	
	println(items.filterIsInstance<String>())
	// [하나, 셋] 
}
```

```kotlin
inline fun <reified T>
        Iterable<*>.filterIsInstance(): List<T> {
	val destination = mutableListOf<T>()
	for (element in this) {
	    if (element is T) {
    	    destination.add(element)
		}
	}
    return destination
}
```


### 11.2.3 클래스 참조를 재정의된 유형 매개변수로 대체하여 `java.lang.Class` 피하기

```kotlin
val serviceImpl = ServiceLoader.load(Service::class.java)
val serviceImpl = loadService<Service>()
```

자바에서는 타입 매개변수를 타입의 인자를 통해 서비스의 유형을 가져오는 방식을 사용했다. 하지만 코틀린에서는 재너릭을 활용해 이를 더 쉽게 구현할 수 있다.

구현된 과정은 아래와 같다.

```kotlin
inline fun <reified T> loadService() {
    return ServiceLoader.load(T::class.java)
}
```

> Android에서의 startActivity함수 단순화>
>
> 안드로이드 개발자라면 익숙한 아래의 예제가 있다.
```kotlin
inline fun <reified T : Activity> Context.startActivity() {
    val intent = Intent(this, T::class.java)
    startActivity(intent)
}
startActivity<DetailActivity>()
```

### 11.2.4 `Reified` 유형 매개 변수로 접근자 선언하기

인라인 함수를 통해 함수 클래스에 접근할 수 있으며, 프로퍼티 접근자가 게터와 세터에 대한 커스텀 구현을 제공할 수 있기에 아래와 같은 구현이 가능하다.

```kotlin
inline val <reified T> T.canonical: String
	get() = T::class.java.canonicalName
    
fun main() {
	println(listOf(1, 2, 3).canonical)
    // java.util.List
    println(1.canonical)
    // java.lang.Integer
}
```

## 11.3 Variance(변성)는 일반 인수 간의 하위 유형화 관계를 설명한다.

`variance`의 개념은 유형이 같고 유형 인수가 다른 유형 (예:`List<String>` 및`List<Any>`)가 서로 어떻게 관련되는지를 설명한다.

### 11.1.1 variance(변성)는 함수에 인수를 전달하는 것이 안전한지를 결정한다.

```kotlin
fun printContents(list: List<Any>) { 	
	println(list.joinToString())
}

fun main() { 
	printContents(listof("abc", "bac")) // abc, bac
}
```

위의 함수는 잘 작동한다. 아니 잘 작동하는 것처럼 보인다. 

아래와 같이 코드를 작성한다면 이는 런타임 오류를 발생시킬 것이다.

```kotlin
fun addAnswer(list: MutableList<Any>) {
    list.add(42)
}

fun main() {
    val strings = mutableListOf("abc", "bac")
    addAnswer(strings)
    println(strings.maxBy { it.length })
    // ClassCastException: Integer cannot be cast to String
}
```

위의 예제는 `MutableList<String>`라는 가변 문자열 리스트를 선언한다. 그런 다음 함수에 전달 하려고 한다. 컴파일러가 이를 허용한다면 문자열 목록에 정수를 추가할 수 있고, 그러면 목록의 내용을 문자열로 액세스하려고 할 때 런타임 예외가 발생할 수 있다.

이러한 이유로 위 예제는 컴파일되지 않는다. 이 예는 `MutableList<Any>`가 예상되는 경우 `MutableList<String>`을 인수로 전달하는것이 안전하지 않다는 것을 보여 주며, `Kotlin` 컴파일러는 이를 금지한다. 

![](https://velog.velcdn.com/images/cksgodl/post/252237a6-6419-4557-b426-e2caeb92f07d/image.png)

`Kotlin`에서는 목록이 변경 가능한지 여부에 따라 적절한 인터페이스를 선택하여 이를 제어해야 한다.

이 섹션의 뒷부분에서는 `List`뿐만 아니라 모든 제네릭 클래스에 대해 동일한 질문을 일반화하겠다. 또한 두 인터페이스인 `List`와 `MutableList`가 타입 인자와 관련하여 왜 다른지도 살펴볼 것이다.

### 11.3.2 클래스, 타입 및 하위 타입 간의 차이점 이해하기

논 제네릭 클래스를 사용하면 클래스 이름을 직접 타입으로 사용 할 수 있다. 
예를 들어 `kotlin
var x: String
`를 작성하면 `String` 클래스의 인스턴스를 보유할 수 있는 변수를 선언하는 것이다.
그러나 동일한 클래스 이름을 사용하여 널 가능 유형을 선언할 수도 있다(예: `var x: String?` 즉, 각 `Kotlin` 클래스는 최소 두 가지 타입을 구성할 수 있다.

제네릭 클래스를 사용하면 이야기는 훨씬 더 복잡해진다. 
  
유형 간의 관계를 논의하기 위해서는 하위 유형이라는 용어에 익숙해져야한다.
`A` 타입의 값이 필요할 때 마다 `B`타입의 값을 사용할 수 있다면 `B` 타입은 `A` 타입의 하위타입이다. 예를 들어 `Int`는 `Number`의 하위 타입이지만 `Int`는 `String`의 하위 타입이 아니다. 

![](https://velog.velcdn.com/images/cksgodl/post/384069ec-d3eb-46bd-a52e-42ad3e61035e/image.png)

컴파일러는 변수에 값을 할당하거나 함수에 인수를 전달할 때마다 이 타입검사를 수행한다. 

```kotlin
fun test(i: Int) {
	val n: Number = i // 컴파일 O
    fun f(s: String) { /*...*/ }
    
    f(i) // 컴파일 X
}
```

![](https://velog.velcdn.com/images/cksgodl/post/245ee25e-be7c-4e3f-aa20-03697d40134e/image.png)

널이 아닌 타입은 널 가능 타입의 하위 타입이지만 둘 다 하나의 클래스에 해당한다. 널러블이 아닌 타입의 값은 항상 널러블 타입의 변수에 저장할 수 있다.

```kotlin
val s: String  = "abc"
val t: String? = s
// This assignment is legal because String is a subtype of String?.
```

리스트의 경우는 다르게 작동한다. `MutableList<Any>`는 `MutableList<String>`의 서브타입이 아니다. 위와같이 불변으로 설정된 제네릭 클래스는 서브타입이나 슈퍼타입일 경우 모두 대입할 수 없다. (이를 불변이라고 한다.)

### 11.3.3 공변성은 하위 유형 관계를 유지한다.

```kotlin
interface Producer<out T> { 
	fun produce(): T
}
```

`Kotlin`에서 클래스를 특정 유형 매개 변수에 대해 공변량으로 선언하려면 유형앞에  `out`키워드를 사용한다.

여기서 공변성은 다음을 의미한다.

>`A`가 `B`의 서브타입인 경우 `Producer<A>`는 `Producer<B>`의 서브타입이며, 우리는 서브타입이 보존된다고 말하고, 이를 공변성을 유지한다라고 한다.

```kotlin
class Cat : Animal() {
    fun cleanLitter() { /* ... */ }
}

class Herd<out T : Animal> {
	
}

fun takeCareOfCats(cats: Herd<Cat>) {
    for (i in 0..<cats.size) {
        cats[i].cleanLitter()
    }
    feedAll(cats)
}
```

 특정 타입 매개변수에 대해 클래스 공변성을 만들면 클래스에서 이 타입 매개변수의 가능한 용도가 제한된다. 유형 안전성을 보장하기 위해 아웃 위치에서만 사용할 수 있으며, 이는 클래스가 유형 `T`의 값을 생성할 수는 있지만 소비할 수는 없음을 의미한다.
 
![](https://velog.velcdn.com/images/cksgodl/post/6f1137af-e181-4e1e-a928-755a78938d00/image.png)

위의 `Herd` 클래스를 다시 보자. 이 클래스는 유형 매개변수`T`를 오직한 곳, 즉 `get` 메서드의 반환값에만 사용할 수 있다.

```kotlin
class Herd<out T : Animal> {
	val size: Int get() = /* ... */
	operator fun get(i: Int): T { /* ... */ } 
}
```

다시 말하자면, 유형 매개변수 `T`의 `out` 키워드는 두 가지 의미를 갖는다

- 하위 유형이 유지(`Producer<Cat>`은 `Producer<Animal>`의 하위 유형)
- `T`는 아웃 위치에서만 사용할 수 있다.

`List`는 `Kotlin`에서 읽기 전용이므로 유형 `T`의 요소를 반환하는 `get` 메서드가 있지만 목록에 유형 `T`의 값을 저장하는 메서드는 정의되어 있지 않다. 따라서 공변성이 있다.

```kotlin
interface List<out T> : Collection<T> {
   
   operator fun get(index: Int): T
   
   fun subList(fromIndex: Int, toIndex: Int): List<T>
   
   // ...
}
```

`MutableList<T>`는 유형 매개변수에 공변수로 선언할 수 없는데, 이는 유형 `T`의 값을 매개변수로 받아 해당 값을 반환하는 메서드가 포함되어 있기 때문이다.

이 유형변수를 생성자에서도 활용할 수 있는데, 이때도 `out`로 선언하여 사용할 수 있다.

```kotlin
class Herd<out T: Animal>(vararg animals: T) { /* ... */ }
```

하지만 `var` 키워드를 사용하는 경우 프로퍼티에 대한 `get`, `set`을 모두 선언하게 됨으로 읽기 전용 속성인 `out`, 변경 가능한 속성인 `in`이 모두 사용되게 되어 `out`으로 표현할 수 없다.

```kotlin
// 불가능
class Herd<T: Animal>(var leadAnimal: T, vararg animals: T) { /* ... */ }
```

하지만 비공개 메서드의 매개 변수로 활용하게 된다면 `in`으로 설정할 수 있다.

```kotlin
class Herd<out T: Animal>(private var leadAnimal: T, vararg animals: T) { /* ... */ }
```

### 11.3.4 Contravariance(반공변성)은 하위 유형화 관계를 역전시킨다.

```kotlin
interface Comparator<in T> {
	fun compare(e1: T, e2: T): Int { /* ... */ } 
}
```

이 인터페이스의 메서드는 `T` 타입의 값만 사용한다는 것을 알 수 있다. 즉, `T`는 `in` 위치에서만 사용되므로 선언앞에 `in` 키워드를 붙일 수 있다.

```kotlin
sealed class Fruit {
	abstract val weight: Int
}

data class Apple(
	override val weight: Int,
	val color: String,
): Fruit()
    
data class Orange(
	override val weight: Int,
    val juicy: Boolean,
): Fruit()
```

![](https://velog.velcdn.com/images/cksgodl/post/78d357a7-c57d-4630-8af6-a4d9f0b69b97/image.png)

`in` 키워드는 해당 타입의 값이 클래스의 메서드로 전달되어 해당 메서드에서 사용됨을  의미한다. 공변성의 경우와 유사하게, 형 매개변수의 사용을 제한하면 특정 서브타입 관계가 발생한다. 타입 매개변수 `T`의 `in` 키워드는 서브타입이 역전되어 `T`는 `in`의 하위타입만 사용할 수 있음을 의미한다.

![](https://velog.velcdn.com/images/cksgodl/post/cf65f839-c7e5-4f9d-843e-26e3dd709117/image.png)

클래스나 인터페이스는 한 유형 매개변수에서는 공변성이고 다른 매개변수에서는 반공변성일 수 있다.

```kotlin
interface Function1<in P, out R> {
    operator fun invoke(p: P): R
}
```

### 11.3.6 "*" 문자를 사용하여 일반 인수에 대한 정보가 부족함을 나타낸다.

알 수 없는 유형의 리스트 목록은 `List<*>`로 표현된다.

__`MutableList<*>`는 `MutableList<Any?>`와 동일하지 않다.__

`MutableList<T>`에서 `T`는 불변이다. `MutableList<Any?>`는 모든 유형의 요소를 포함할 수 있는 목록이다. 반면에 `MutableList<*>`는 사용자가 모르는 특정 유형의 요소를 포함하는 목록이다.

```kotlin
fun main() {
	val list: MutableList<Any?> = mutableListOf('a', 1, "qwe")
	val chars = mutableListOf('a', 'b', 'c')
	val unknownElements: MutableList<*> =
        if (Random.nextBoolean()) list 
        else chars
	
    println(unknownElements.first())
	// a
	unknownElements.add(42)
	// Error: Out-projected type 'MutableList<*>' prohibits
	// the use of 'fun add(element: E): Boolean'
}
```

이 문장에서 `MutableList<*>`는 `MutableList<out Any?>`로 투영(작동)된다. 요소의 타입에 대해 아무것도 모르는 경우 `Any?` 유형의 요소를 가져오는 것은 안전하지만 유형을 목록에 넣는 것은 안전하지 않다.

```kotlin
    fun printFirst(list: List<*>): Any? {
        if (list.isNotEmpty()) {
            return list.first()
        }
    }
```

### 11.3.7 Type aliases

`typealias` 키워드를 사용하여 유형 별칭을 도입한 다음 그 뒤에 별칭을 지정할 수 있다.

```kotlin
typealias NameCombiner = (String, String, String, String) -> String
val authorsCombiner: NameCombiner = { a, b, c, d -> "$a et al." }
val bandCombiner: NameCombiner = { a, b, c, d -> "$a, $b & The Gang" }

fun combineAuthors(combiner: NameCombiner) {
    println(combiner("Sveta", "Seb", "Dima", "Roman"))
}

fun main() {
    combineAuthors(bandCombiner)
    // Sveta, Seb & The Gang
    combineAuthors(authorsCombiner)
    // Sveta et al.
    combineAuthors { a, b, c, d -> "$d, $c & Co."}
    // Roman, Dima & Co.
}
```

`typealias`을 도입함으로써 함수형 유형에 코드를 읽는데 도움이 될 수 있는 추가 컨텍스트를 불어넣을 수 있다.

> 인라인 클래스 및 타입얼라이스
`typealias`는 유용한 약어를 제공하지만 추가적인 유형 안전성을 제공하지는 않는다. 
> 따라서 런타임 오버헤드를 최소화하면서 유형 안전성을 추가하는 것이 목표라면 인라인 클래스를 사용해야 한다.
```kotlin
@JvmInline
value class ValidatedInput(val s: String)
fun save(v: ValidatedInput): Unit = TODO()
fun main() {
    val rawInput = "needs validating!"
    save(rawInput)
}
```
> 하지만 람다와 같은 형식의 컨텍스트 명을 변경해야할 때는 `typealias`를 사용하자.

## 요약

- `Kotlin`의 제네릭은 `Java`의 제네릭과 매우 유사하다. 동일한 방식으로 제네릭 함 수 또는 클래스를 선언한다.
- `Java`에서와 마찬가지로 일반 유형에 대한 유형 인수는 컴파일 시에만 존재한다.
- 유형인수는 런타임에 지워지므로 유형인수가 있는 유형을 `is` 연산자와함
께 사용할 수 없다.
- 인라인 함수의 유형 매개변수를 재정의된 것으로 표시할 수 있으므로 런타임에 이를 사용하여 `is` 검사를 수행하고 `java.lang.Cl`ass 인스턴스를 가져 올 수 있다.
- 변성은 기본클래스가 같고 타입 인자가 다른 두 제네릭 타입중 하나가 다른 타입 인자의 서브타입일 때 다른 타입의 서브타입인지 슈퍼타입인지 지정하는 방법이다.
- 매개변수가 `out` 위치에서만 사용되는 경우 유형 매개변수에 대한 공변성로 클래스를 선언할 수 있다.
- 반공변성의 경우는 그 반대이다. 클래스 매개변수가 `in` 위치에서만 사용되는 경우 유형 매개변수에서 클래스를 반공변성으로 선언할 수 있다.
- `Kotlin`의 읽기 전용 인터페이스 `List`는 가변형으로 선언되며, 이는 다음을 의미한다. `List<String>`은 `List<Any>`의 하위유형이다.
- 별표 투영구문은 정확한 유형인수를 알 수 없거나 중요하지 않은 경우에 사용할 수 있다.
- `typealias`을 사용하면 유형에 대한 대체 또는 단축된 이름을 제공할 수 있다. 컴 파일 시 기본 유형으로 변경된다.
 
 
 
 