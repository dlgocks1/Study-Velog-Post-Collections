### Generic이 무엇인가?


**Generic** : 포괄적인, 총칭의(네이버사전)

제너릭이란 데이터 형식에 의존하지 않고, 하나의 값이 여러 다른 데이터 타입들을 가질 수 있도록 하는 방법이다.

즉 그릇만 미리 생성하고 여기에는 무슨 과일이 들어갈 거예요. 라고 이름표를 나중에 붙이는 느낌

정리하자면
> 제네릭은 클래스 내부에서 사용할 자료형을 나중에 인스턴스를 생성할 때 확정한다.

```
// <> 안에 형식 매개변수를 넣어 선언하
class TestClass<T>(t: T) {
    var value = t
}
// ,를 이용하여 여러개의 형식 매개변수를 사용할 수 있다.
class TestClass<S, T>(s : S,t: T) {
    var value = t
}
```

객체의 자료형을 **컴파일 타임**에 체크하기 때문에 객체 자료형의 안정성을 높이고 형 변환의 번거로움이 줄어든다.

## 제너릭 클래스
코틀린에서의 클래스는 자바와 같이 타입파라미터를 가진다.

### 타입파라미터란?
* <> 안에 들어가는 파라미터를 의미

![](https://velog.velcdn.com/images/cksgodl/post/e5906692-ccff-49e1-aeaf-22841fe11ab0/image.png)

이는 임의로 사용자가 결정한 것이며, 암시적으로 사용하는 룰이다.

```
fun main() {
	// 직접 명시할 수도있고
    var testvar : TestClass<Int> = TestClass(1)
    // 타입추론이 가능하면 생략가능
    var testvar2 = TestClass("2")
}

class TestClass<T>(t: T) {
    var value = t
}
```
---

코드를 작성하다 보면 다양한 타입에 동일한 로직을 적용하기 위해 코드 재사용을 과도하게 하려는 경우가 있다.

이를 테면 파라미터를 전부 Any 로 받는다거나 등 이런 경우에는 타입 안정성을 저하시킬 수가 있다.

### 제네릭을 사용하는 이유
1. 컴파일 타임에 강력한 타입 검사
2. 캐스팅(타입 변환) 제거

---

다음과 같은 소스는 정상 작동할까?
```
val objectList : Object = ArrayList<Int>()
```
Object는 최상위 자료형임으로 가능할 것 같다. 라고 생각할 수 있지만
```
Type mismatch: inferred type is kotlin.collections.ArrayList<Int> /* = java.util.ArrayList<Int> */ but Object was expected
```
아쉽게도 오류가난다.

그렇다면 이건 어떨까?
```
val objectList2 : List<Object> = ArrayList<Int>()
```
Object는 Int의 상위 타입으로 오류가 안날 것 같지만
```
Type mismatch: inferred type is Int but Object was expected
```
이또한 오류를 발생시킨다.

이는 제네릭 타입의 특징때문인데
object가 Int형의 상위 타입이여도 
List<Object\>는 ArrayLIst<Int\>의 상위 타입이 아니기 떄문이다. 아무런 관계가 없다.

이 개념은 변성이라는 개념과 관계있다.
### 무변성, 공변성(corvariance), 반공변성과

#### 무변성(무공변)이란?
자료형의 상하관계를 잘 이용해도 타입 캐스팅이 불가능한 것을 무변성 즉 변하지 않는 성질이라고 한다.
* List<Object\> 와 ArrayList<Int\>의 예제가 이에 통한다.
  
#### 반공변성이란? <? in T>
상위 자료형을 하위 자료형으로 할당가능 한것을 의미한다.

#### 공변성이란?? <? out T>
X -> Y로 객체변환이 가능할 때 C<X\> -> C<Y\>이면 이를 공변하다고 한다
.
다시 말하면 **하위 자료형을 상위 자료형으로 할당이 가능한 것을 의미한다.**
```
// 하위 자료형인 Int를 Object에 할당이 가능하다.
val objectArr : Object = 5 
```  

### null과 Generic
 Any타입은 null을 사용할 수 없다. Any자료형을 이용하여 모든 변수를 받아버리면 null값을 넣을 때 오류가 발생한다.

제네릭은 nullable 자료형임으로 null값을 넣어도 정상 작동하는 것을 볼 수 있다.
```
fun main() {
    val obj = testClass<Int?>()
    obj.func1(null) // print null

    val obj2 = testClass2<Int?>()
    obj.func1(null) // Error
}

class testClass<T>{
    fun func1(arg1 : T){
        println(arg1)
    }
}

// :을 사용하여 제네릭의 타입 제한
class testClass2<T : Any>{
    fun func1(arg1 : T){
        println(arg1)
    }
}

```

### Generic의 자료형 제한
위의 소스에서 볼 수 있듯이 <T: Any>처럼 제너릭의 자료형에 제한을 둘 수 있다. 

```
class Calc<T : Number> {
    fun plus(arg1: T, arg2: T): Double {
        return arg1.toDouble() + arg2.toDouble()
    }
}
```
Number 클래스에 들어갈 수 있는 것
![](https://velog.velcdn.com/images/cksgodl/post/fe8f09e5-c92f-41a3-86a1-a7ead66aab8b/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/f9ded02c-3550-4e0a-9861-cdda198336cc/image.png)

Char, Short, Byte는  변환되어 나온다고 한다.

### 제너릭 변수를 이용한 계산
```
class Calc<T>(){
    fun add(a : T, b : T){
        println(a+b)
    }
    // receiver type mismatch
}
```
이 함수는 잘 작동할까?
정답은 X 이다.
이는 제너릭의 자료형을 결정할 수 없으므로 오류가 난다.

```
fun main() {
    println(add(2,5){
        i, i2 ->
        i+i2
    })
}

fun <T>add(a : T,b: T,sum : (T,T) -> T) : T {
    return sum(a,b)
}
```
그러나 람다식을 이용하여 매개변수를 받으면 실행 시 람다식 본문을 넘겨줄 때 자료형이 결정됨으로 문제가 되지 않는다.




---

예시를 보며 이해해보자.

Fruite이라는 클래스를 상속받는 Apple, Banana클래스를 생성해보자.
```
open class Fruit
class Apple : Fruit()
class Banana : Fruit()
```
부모관계는 Fruite > Apple = Banana 일 것이다.

```
fun main() {
    val fruits: Array<Apple> = arrayOf(Apple())
    receiveFruits(fruits) // Error!!
}

fun receiveFruits(fruits: Array<Fruit>) {
    println("Number of fruits: ${fruits.size}")
}
```  
다음과 같은 소스는 오류가 난다. 

왜냐하면 Fruit 클래스를 제네릭 타입으로 선언된 배열(Array)을 파라미터로 받는 receiveFruits() 함수에 Array<Apple\>을 전달하고자 하였기 때문이다.

_**아니 Apple이 Fruite을 상속받는데도 왜 전달이 안되지?** _

이런 제약은 코틀린이 가진 제네릭에 대한 타입 불변성 때문에 발생한다.

```
fun main() {
    val fruits: Array<Apple> = arrayOf(Apple())
    receiveFruits(fruits)
}
 
fun receiveFruits(fruits: Array<Fruit>) {
	fruits[0] = Banana() // Error!!
}
```
Apple클래스를 전달하여 Banana클래스를 담을 때 문제가 발생한다.

```
fun receiveFruits(fruits: List<Fruit>) {
    println("Number of fruits: ${fruits.size}")
}
 
fun main() {
    val fruits: List<Apple> = listOf(Apple(), Apple())
    receiveFruits(fruits)   // Number of fruits: 2
}
```
### Kotlin에서의 와일드 카드
 * <*> : UnBounded WildCards (제한 없음)
Java에서는 <?> 로 쓰이며 읽기/쓰기가 가능합니다.
* < out T > : Upper Bounded WildCards (상위 클래스 제한)
Java에서는 <? extends T> 로 쓰이며 읽기만 가능합니다.
![](https://velog.velcdn.com/images/cksgodl/post/ff25ffa3-285d-41f4-9ef0-32f1e8ee670c/image.png)


* < in T > : Lower Bounded WildCard (하위 클래스 제한)
Java에서는 <? super T> 로 쓰이며 쓰기만 가능합니다.
  ![](https://velog.velcdn.com/images/cksgodl/post/97c637e4-2e49-405c-9fb9-f43362f4d773/image.png)

  
  
### 사용 지점 변성 out, in

그러나 mutable하지 않은, 즉 Writing이 되지않는 List를 사용해 함수를 실행하면 이는 작동한다.
Array<T\>는 class Array<T\> 로 정의되어 있고, List<T\> 는 interface List<out E\> 로 정의되어 있기 때문이다.

>코틀린 에서는 T 가 값을 리턴 (produce) 만 할뿐 데이터 변경 (consume) 은 일어나지 않는 것을 **out**을 사용해 명시할 수 있다.


```
// out으로 값을 리턴만 할것을 정의
interface Source<out T> {
    fun nextT(): T
}

fun demo(strs: Source<String>) {
    val objects: Source<Any> = strs // This is OK, since T is an out-parameter
    // ...
}
```
out 은 variance annotation 이라 불리며 type parameter 의 선언부에 사용되기 때문에 declaration-site variance 라고 부른다.

```
interface Comparable<in T> {
    operator fun compareTo(other: T): Int
}

fun demo(x: Comparable<Number>) {
    x.compareTo(1.0) // 1.0 has type Double, which is a subtype of Number
    // Thus, you can assign x to a variable of type Comparable<Double>
    val y: Comparable<Double> = x // OK!
}
```
* in 은 반공변적(contravariant)선언 하한경계

* out 의 consume only, never produce 상한경계 의미

읽기 전용은 안에 들어있는 값을 빼서 읽어야 하니까 **out**,
쓰기 전용은 새로운 값을 집어 넣어야 하니까 **in**

**PECS**
produser - out
consumer - in

상한경계를 걸어서 개체 값을 안전하게 가져오기
![](https://velog.velcdn.com/images/cksgodl/post/8dedece1-d94c-4af9-9aa7-6a9ee0fd1bca/image.png)

t는 하한경계, u는 상한경계
![](https://velog.velcdn.com/images/cksgodl/post/9095f00e-e964-4c5f-a6d4-aebc1e1263ce/image.png)



### Generic function

클래스 뿐만 아니라 함수도 type parameter을 가질 수 있다.

type parameter 는 함수의 이름 앞에 위치한다.

![](https://velog.velcdn.com/images/cksgodl/post/a7abb682-0cbc-41fd-b593-7521f67aa427/image.png)

```
fun <T> singletonList(item: T): List<T> {
    // ...
}
fun <T> T.basicToString(): String { // extension function
    // ...
}

val l = singletonList<Int>(1)
// 타입추론이 가능할 때는 생략 가능
val l = singletonList(1)
```


콜론 ":" 뒤에 지정된 것이 upper bound이며, 이는 upper bound의 하위type만이 T로 지정될 수 있다는 것을 의미한다.

_<T\>는 T로 치환할 수 있다._

```
fun <T : Comparable<T>> sort(list: List<T>) {  ... }

// Int는 Comparable<Int>의 하위객체여서 가능하다.
sort(listOf(1, 2, 3)) 

// 오류: HashMap<Int, String>은 Comparable<HashMap<Int, String>>의 하위 객체가 아니기 때문에 불가능하다.
sort(listOf(HashMap<Int, String>()) 
```

아무것도 지정하지 않으면 기본 upper bound 는 Any? 이다.

< > 안에는 하나의 upper bound 만 쓸수있다.

같은 type parameter 가 한개 이상의 upper bound 가 필요하면 where 구문으로 구분할 수 있다

```
fun <T> copyWhenGreater(list: List<T>, threshold: T): List<String>
    where T : CharSequence,
          T : Comparable<T> {
    return list.filter { it > threshold }.map { it.toString() }
}
```


### Generic 프로퍼티 정의하기
프로퍼티는 확장 프로퍼티에 한해서만 Generic하게 만들 수 있다. 
클래스나 함수, 프로퍼티에서 타입 파라미터를 정의하고, 타입 아규먼트는 그 클래스, 함수, 프로퍼티의 외부에서 정해주어야하기 때문이다.
![](https://velog.velcdn.com/images/cksgodl/post/4e9e9ae5-c59b-4781-b7ef-d6a5b9f72c70/image.png)
```
class Box<T> {
    // ERROR : Type parameter of a property must be used in its receiver type
    //val <T> property:T = TODO()
}

// 확장 프로퍼티만 타입 프로퍼티를 사용할 수 있다.
val <T> List<T>.penultimate:T
    get() = this[size-2]

fun main() {
    println(listOf(1,2,3,4).penultimate)
}
```

---
### 실사용 예시

MVVM 구조에서 Databing된 객체의 Event처리를 할 때 EventWrapper클래스를 사용하여 처리하는 과정이다.

```
// Generic Type을 out으로 선언 -> 리턴만 할것을 정의
open class MapEvent<out T>(private val content: T) {
    var hasBeenHandled = false
        private set

    fun getContentIfNotHandled(): T? {
    	// 이벤트가 이미 처리 되었다면
        return if (hasBeenHandled) { 
            null // null을 반환하고,
        } else { 
        	// 이벤트가 처리되었다고 표시한 후에
            hasBeenHandled = true 
            content // 값을 반환합니다.
        }
    }

	// 이벤트의 처리 여부에 상관 없이 값을 반환
    fun peekContent(): T = content
}

// 제너릭 프로퍼티 정의
@MainThread
inline fun <T> LiveData<MapEvent<T>>.eventObserve( 
    owner: LifecycleOwner,
    // crossinline 으로 함수형 파라미터를 non-local이 아닌 곳에서 사용 
    crossinline onChanged: (T) -> Unit
): Observer<MapEvent<T>> {
    val wrappedObserver = Observer<MapEvent<T>> { t ->
        t.getContentIfNotHandled()?.let {
        	// it : T & Any
            onChanged.invoke(it)
        }
    }
    observe(owner, wrappedObserver)
    return wrappedObserver
}
```

* crossinline이란??
함수에서 다른 고차함수를 호출할 때, 그 안에서 함수형 파라미터인 func를 실행하고자 할 때 사용
"inline 함수는 함수형 파라미터를 non-local이 아닌 곳에서 호출 할수 없다. func 에 'crossinline' 을 추가하여 사용

```
	// In ViewModel
    private val _telEvent = MutableLiveData<MapEvent<String>>()
    val telEvent : LiveData<MapEvent<String>> get() = _telEvent
    fun onTelEvent(text : String){
        _telEvent.value = MapEvent(text)
    }
```

In MapActivity
```
mapViewModel.telEvent.eventObserve(this) { it ->
            startActivity(Intent(Intent.ACTION_DIAL, Uri.parse("tel:" + it.replace("-", ""))))
            }
```

In XML
```
<TextView
android:layout_width="wrap_content"
android:layout_height="wrap_content"
android:onClick="@{() -> mapViewModel.onTelEvent(mapViewModel.telno)}"
android:text="@{mapViewModel.telno}"
/>
```

### 정리

1. 비슷한 기능을 구현하는 경우 코드의 재사용성이 높아진다.

2. 제네릭을 사용할 때는 공변선을 해치지 않게 declaration-site variance을 사용하며 조절한다.

3. 클래스 외부에서 타입을 지정해주기 때문에 따로 타입을 체크하고 변환해줄 필요가 없다. 즉, 관리하기가 편하다.




