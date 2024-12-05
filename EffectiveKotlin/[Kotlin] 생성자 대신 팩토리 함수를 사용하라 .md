클래스의 인스턴스를 만드는 가장 간단한 방법은 생성자를 사용하
는 방식이다.

```kotlin
Class MyLinkedList<T>(
	val head: T,
    val tail: MyLinkedList<T>?
)

val list = MyLinkedList(1, MyLinkedList(2, null))

```

이러한 생성자는 자바에서도 사용된 방식이고 익숙한 방법일 것이다.

하지만 생성자가 객체를 만들 수 있는 유일한 방법은 아니다. `디자인패턴`으로 다양한 생성 패턴이 있기 때문이다. 이러한 생성 패턴은 객체를 생성자로 직접 생성하지 않고, 별도의 함수를 통해 생성한다. 
예를 들어 다음 함수를 보자.

```kotlin
fun <T> myLinkedListOf(
	vararg elements: T		// 가변인자로 변수 여러개 할당 가능
): MyLinkedList<T>?{
	if(elements.isEmpty()) return null
    val head = elements.first()
    val elementsTail = elements.compyOfRange(1, elements.size) // 첫번 째 원소를 제외한 나머지를 꼬리로 취급
    val tail = myLnikedListOf(*elementsTail)
    return MyLinkedList(head, tail) // 이제서야 생성자로 객체 생성
}

val list = myLinkedListOf(1, 2)
```
myLinkedListOf() 톱레밸 함수는 클래스의 인스턴스를 만들어서 반환해준다.

생성자의 역할을 대신 해주는 함수를 `팩토리 함수`라고 부른다.

### 왜 팩토리 함수를 사용해야 할까?


1. 생성자와 다르게 함수에 이름을 붙일 수 있다.
ArrayList(3)이라는 코드가 3이라는 원소를 가진 배열인지, 3개의 사이즈를 가진 배열인지 모호할 수도 있다. 하지만 ArrayList.withSize(3)이라는 함수로 구현한다면 이는 훨씬 이해하기 쉬울 것이다.

2. 생성자와 다르게, 함수가 원하는 형태의 타입을 리턴할 수 있다. 즉 다른 객체를 생성할 때 사용할 수 있다. `listOf`함수를 생각해보자 이는 List 인터페이스를 리턴하며 이는 각각의 플랫폼에 따라 다른 리턴값을 가진다. (코틀린/JVM, 코틀린/JS, 코틀린/네이티브에 따라서 각 플랫폼의 빌트인 컬렉션으로 제공됨)
```kotlin
// JVM에서의 listOf
public fun <T> listOf(element: T): List<T> = java.util.Collections.singletonList(element)
```

3. 생성자와 다르게, 호출될 때마다 새 객체를 만들 필요가 없다. 함수를 사용해 객체를 생성하면 싱글턴 패턴처럼 하나만 생성하게 강제하거나, 최적화를 위해 캐싱 메커니즘을 사용할 수 있다고 한다.
객체를 만들 수 없을 때 null을 리턴하게 한다던가 사용자에게 선택지가 생긴다.

4. 팩토리 함수는 아직 존재하지 않는 객체를 리턴할 수 있다. 이를 통해 프로젝트를 빌드하지 않고도 앞으로 만들어질 객체를 사용할 수 있다.

5. 객체 외부에 팩토리 함수를 만들면 가시성을 원하는대로 제어 할 수 있다.

6. 팩토리 함수는 인라인으로 만들 수 있으며, 그 파라미터들을 reified로 만들 수 있다.
> reified를 사용하면 제너릭 타입을 사용하며, 해당 파라미터의 클래스에 접근가능하다. 이는 inline함수와 같이 사용되어야 한다.

7. 팩토리 함수는 생성자로 만들기 복잡한 객체도 만들 수 있다.

8. 생성자는 즉시 슈퍼클래스 또는 기본 생성자를 호출하지만, 팩토리 함수는 그럴필요가 없다.

## 팩토리 함수의 종류에는 무엇이 있을까

#### 1. Companion 객체 팩토리 함수

팩토리 함수를 정의하는 가장 일반적인 방법은 companion객체를 사용하는 것이다.

```kotlin
class MyLinkedList<T>(
    val head: T,
    val tail: MyLinkedList<T>?
){
    companion object{
        fun <T> of(vararg elements: T): MyLinkedList<T>?{
            if(elements.isEmpty()) return null
            val head = elements.first()
            val elementsTail = elements.copyOfRange(1, elements.size) // 첫번 째 원소를 제외한 나머지를 꼬리로 취급
            val tail = of(*elementsTail)
            return MyLinkedList(head, tail) // 이제서야 생성자로 객체 생성
        }
    }
}

val list = MyLinkedList.of(1,2,3) 

```

이는 자바의 정적 팩토리 함수와 같다. 코틀린에서는 이러한 접근 방법을 인터페이스에도 구현할 수 있다.

```kotlin
interface MyList<T>{
    companion object{
        fun <T> of(vararg elements: T): MyLinkedList<T>?{
            if(elements.isEmpty()) return null
            val head = elements.first()
            val elementsTail = elements.copyOfRange(1, elements.size) 
            val tail = of(*elementsTail)
            return MyLinkedList(head, tail) 
        }
    }
}

val myLIst = MyList.of(1,2,3)
```

함수의 이름에는 다음과 같은 컨벤션이 정해져 있다.

* from : 파라미터를 하나 받고, 같은 타입의 인스턴트를 리턴한다.
```kotlin
val date: Date = Date.from(instant)
```

* of : 파라미터를 여러 개 받고, 이를 통합해서 인스턴트를 만든다.
```kotlin
val faceCards: Set<Rank> = EnumSet.of(JACK, QUEEN, KING)
```

* valueOf : from 또는 of와 비슷한 기능을 하면서도, 의미를 조금 더 쉽게 읽을 수 있게 이름을 붙인 것
```kotlin
val prime: BigInteger = BigInteger.valueOf(Integer.MAX_VALUE)
```
* instnace 또는 getInstance : 싱글톤으로 인스턴스를 하나 리턴하는 함수

```kotlin
val luke: StackWalker = StacakWalker.getInstance(options)
```

* createInstance 또는 newInstance : getInstance처럼 동작하지만, 싱글톤이 아니라 호출할 때 마다 새로운 인스턴스 값 리턴

```kotlin
val newArray = Array.newInstance(classObject, arrayLen)
```


* getType: getInstance처럼 동작하지만, 팩토리 함수가 다른 클래스에 있을 때 사용하는 이름이다.

```kotlin
val fs: FileStore = Files.getFileStore(path)
```

* newType : newInstance처럼 동작하지만, 팩토리 함수가 다른 클래스에 있을 때 사용하는 이름이다.

```kotlin
val br: BufferedReader = Files.newBufferedReader(path)
```


#### 2. 확장 팩토리 함수

Platton 인터페이스를 수정하지 않고도 확장 함수를 이용해 Squad객체를 찍어낼 수 있다.

```kotlin
data class Squad(
    val leader: String,
    val count: Int
)

interface Platton{
    companion object{
    }
}

fun Platton.Companion.createSquad(leader: String, count: Int): Squad{
    return Squad(leader = leader, count = count)
}

val squad1 = Platton.Companion.createSquad("Lee",5)
```
하지만 이러한 방법을 활용하려면 인터페이스에 적어도 비어있는 컴패니언 객체가 필요하다.
```kotlin
interface Platton{
    companion object{
    }
}
```

#### 3. 톱레밸 팩토리 함수
객체를 만드는 흔한 방법 중 하나로 listOf, setOf, mapOf등이 모두 다 톱레밸 팩토리 함수이다.

```kotlin
@kotlin.internal.InlineOnly
public inline fun <T> listOf(): List<T> = emptyList()

@kotlin.internal.InlineOnly
public inline fun <T> setOf(): Set<T> = emptySet()
```

public한 톰레벨 함수는 모든 곳에서 사용할 수 있으므로, IDE가 제공하는 팁을 복잡하게 만든다. 

#### 4. 가짜 생성자

코틀린에서 생성자는 톱레밸 함수와 같은 형태로 사용된다.
```kotlin
class A
val a = A()
```

보통 개발자의 관점에서 대문자로 시작하는지 아닌지는 생성자와 함수를 구분하는 기준이다. 함수도 대문자로 시작할 수 있지만, 이는 특수한 다른 용도로서 사용된다.
예를들어 List와 MutableList는 인터페이스이며 생성자를 갖리 수 없다. 하지만 List를 생성자처럼 사용하는 코드를 보았을 것이다.

```kotlin
List(4) { it } // 0, 1, 2, 3
```
이는 함수가 코틀린 1.1부터 stdlib에 포함되었기 때문이다.
```kotlinkotlin
public inline fun <T> List(size: Int, init: (index: Int) -> T): List<T> = MutableList(size, init)

public inline fun <T> MutableList(size: Int, init: (index: Int) -> T): MutableList<T> {
    val list = ArrayList<T>(size)
    repeat(size) { index -> list.add(init(index)) }
    return list
```
이러한 톱레밸 함수는 생성자 처럼 보이며, 생성자처럼 작동한다 하지만 팩토리 함수와 같은 모든 장점을 가진다. 많은 개발자가 이것이 톱레벨함수인지, 생성자인지 잘 모르기 때문에 이를 가짜 생성자라고 부른다.

생성자 대신 가짜 생성자를 만드는 이유는 다음과 같다.
* 인터페이스를 위한 생성자를 만들고 싶을 때
* reified 타입 아규먼트를 갖게 하고 싶을 때

nullable 타입 리턴, 캐싱, 서브클래스 리턴등과 같은 기능을 포함하고 싶다면 companion 객체 팩토리 메서드 처럼 다른 이름을 가진 팩토리 함수를 사용하자.


#### 5. 팩토리 클래스의 메서드

```kotlin
data class Student(
	val id: Int,
    val name: String,
    val surname: String
)

class StudentsFactory {
	var nextId = 0,
    fun next(name: String, surname: String) =
    	Student(nextId++, name, surname)
}

val factory = StudentsFactory()
val s1 = factory.next("Marcin", "Moskala")
val s2 = factory.next("Igor"," Wojda")
```

**팩토리 클래스는 클래스의 상태를 가질 수 있다는 특징 때문에 사용된다.**

팩토리 클래스는 프로퍼티를 가질 수 있으며 이를 이용해 다양한 기능을 도입할 수 있다.
* 캐싱을 활용하거나
* 이전에 만든 객체를 복제해서 객체를 생성하는 방법으로 객체 생성 높이기

### 정리

코틀인은 다양한 팩토리 함수를 만들 수 있는 방법을 제공하며 객체를 생성할 때는 이런 특징을 잘 파악하고 사용해야 한다. 

팩토리 함수를 정의하는 가장 일반적인 방법은 companion 객체를 사용하는 것이다. 이 방식은 자바의 정적 팩토리 메서드 패턴과 굉장히 유사하고 코틀린은 자바의 스타일과 관습을 대부분 사용하기 때문이다.



# 기본 생성자에 이름 있는 옵션 아규먼트를 사용하라.

[코틀린에서의 빌더패턴](https://velog.io/@cksgodl/kotlin-kotlin%EC%97%90%EC%84%9C%EC%9D%98-infix-%EB%B0%8F-Builder-%ED%8C%A8%ED%84%B4)

점층적 생성자 패턴 및 빌더 패턴은 코틀린에서 의미가 없다.

### 점층적 생성자 패턴

점층적 생성자 패턴은 `여러가지 종류의 생성자를 사용하는` 패턴을 의미한다.
 
 ```kotlin
class Pizza{
	val olives: Int,
	val cheese: Int
    
    constuctor(size: String, cheese: Int, olives: Int, bacon: Int){
    	this.size = size
        this.cheese = cheese,
        this.olives = olives,
        this.bacon = bacon
    }
    
    consructor(size: String, cheese: Int, olivese: Int):
    	this.size, cheese, olivese, 0)
        
    // ...
}
```

이러한 코드는 코틀린에서 의미가 없는 코드이다. 코틀린에서는 `디폭트 아규먼트`를 지원하기 때문인데

```kotlin
class Pizza(
	val size: String,
    val cheese: Int = 0,
    val olivese: Int = 0,
    val bacon: Int = 0
)
```

디폴트 아규먼트로 코드를 단순화하고 가독성을 높일뿐 아니라 다양한 기능을 제공한다.

```kotlin
val myFavorite = Pizza("L", olives = 3)

val yourFavorite = Pizza("S", olives = 3, cheese = 5)
```
이와 같이 이름이 있는 아규먼트를 넣어서 다음과 같이 초기화할 수도 있다.

디폴트가 아규먼트가 점층적 생성자보다 좋은 이유는 다음과 같다.

* 파라미터들의 값을 원하는 대로 지정할 수 있다.
* 아규먼트를 원하는 순서로 지정할 수 있다.
* 명시적으로 이름을 붙여서 아규먼트를 지정하므로 의미가 명확하다.
```kotlin
val villagePazza = Pizza("L",1,2,3) 
// 1, 2, 3이 무엇을 의미하는지 알 수 없음
// IDE가 설명해 줄 것이지만, 깃허브 등에서 코드를 읽는 사람은 알 수 없다.

val villagePizza = Pizza(
	size = "L",
    cheese = 1,
    olives = 2,
    bacon = 3
) // 훨씬 더 명확함
```

### 빌더 패턴

자바에서는 이름 있는 파라미터 및 디폴트 아규먼트를 사용할 수 없음으로 빌더 패턴을 사용한다.
빌더 패턴을 사용하면 다음과 같은 장점이 있다.
* 파라미터에 이름을 붙일 수 있다.
* 파라미터를 원하는 순서대로 지정할 수 있다.
* 디폴트 값을 지정할 수 있다.

**모두 코틀린의 이름있는 아규먼트에서 지원하는 기능들이다.**

빌더패턴을 코틀린에서 만들어 보면 다음과 같다.

```kotlin
class Pizza private constructor(
	val size: String,
    val cheese: Int,
    val olivese: Int,
    val bacon: Int
) {
	calss Builder(private val size: String) {
    	private var chesse: Int = 0
        private var olives: Int = 0
        private var bacon: Int = 0
        
        fun setCheese(value: Int): Builder = apply {
        	cheese = value
        }
        fun setOlivese(value: Int): Builder = apply {
        	olives = value
        }
        fun setBacon(value: Int): Builder = apply {
        	bacon = value
        }
        
        fun build() = Pizza(size, cheese, olivse, bacon)
    }
}


val villagePizza = Pizza.Builder("L")
	.setCheese(1)
    .setOlives(2)
    .setBacon(3)
    .build()
```

빌더패턴 보다 이름있는 파라미터를 사용하는 것이 좋은 이유를 정리하면 다음과 같다.

* 더 짧고 가독성이 좋으며 코드를 수정하는 것도 쉽다.

* 더 명확하다. 
객체가 생성될 때 빌더패턴은 여러 메서드를 확인해야 하지만, 디폴트 아규먼트가 있는 코드는 생성자 주변만 확인하면 된다.

* 더 사용하기 쉽다.

* 동시성과 관련된 문제가 없다.
코틀린의 함수 파라미터는 항상 `immutable`하지만 대부분의 빌더 패턴에서 프로퍼티는 `mutable`하다. 빌더 패턴의 함수를 쓰레드 안전하게 구현하는 것은 어렵다.


하지만 빌더패턴이 더 좋은 경우도 있다.
다음과 같은 예를 보자, 빌더 패턴은 값의 의미를 묶어서 지정할 수 있다.(setPositiveButton, setNegativeButton, addRoute) 또한 특정 값을 누적하는 형태로 사용될 수 있다.(addRoute)

```kotlin
val dialog = AlertDialog.Builder(context)
	.setMessage(R.string.fire_missiles)
    .setPositiveButton(R.string.fire, {d, id ->
    	// 미사일 발사!
    }
    .setNegativeButton(R.string.cancel, {d, id->
    	// 취소 버튼을 누름
    }
    .create()

val router = Router.Builder()
	.addRoute(path = "/home", ::showHome)
    .addRoute(paht = "/users", ::showUsers)
    .build()
```
빌더 패턴을 사용하지 않고 이를 구현하려면 추가적인 타입들을 만들고 활용해야 한다.
```kotlin
val dialog = AlertDialog(context,
	message = R.string.fire_missiles,
    positiveButtonDescription = 
    	ButtonDescription(R.string.fire, {d , id->
        	// 미사일 발싸!
        }),
   negativeButtonDescription = 
   		ButtonDescription(R.string.cancel, { d, id ->
        	// 사용자가 취소를 누름
        })
  )
  
val router = Router(
	routes = listOf(
    	Route("/home", ::showHome),
        Route("/users", ::showusers)
        )
)
```

이러한 코드는 코틀린 커뮤니티에서 좋게 받아 들여지지 않는다. 일반적으로 다음과 같이 DSl 빌더를 사용한다.

```kotlin
val dialog = context.alert(R.string.fire_missiles) {
	positiveButton(R.string.fire) {
    	// 미사일 발사!
    }
    negativeButton {
    	// 취소 누름
    }
}

val route = router {
	"/home" directsTo :: showHome
    "/users" directsTo :: showUsers
}
```
이렇게 DSL빌더를 활용하는 패턴이 전통적인 빌더 패턴보다 훨씬 유연하고 명확하여 많이 사용한다.
DSL를 만드는 것이 쉬운 것은 아니지만, 시간을 조금 더 투자해서 더 유연하고 가독성이 좋은 코드를 만들어 낼 수 있다면, 그 방법을 사용하는 게 더 좋을 것이다.

### 정리

디폴트 아규먼트는 더 짧고, 더 명확하고, 더 사용하기 쉽다. 또한 빌더패턴을 사용할 이유가 없으며 거의 사용하지 않는다.
빌더 패턴을 사용하는 경우는 다음과 같은 경우이다.
* 빌더 패턴을 사용하는 다른 언어로 작성도니 라이브러리를 그대로 옮길 때
* 디폴트 아규먼트와 DSL을 지원하지 않는 다른 언어에서 쉽게 사용할 수 있게 API를 설계할 때

이를 제외하면 빌더 패턴 대신에 디폴트 아규먼트를 갖는 기본 생성자 또는 DSL를 사용하는 것이 좋다.








참고 자료 

https://boilerplate.tistory.com/57