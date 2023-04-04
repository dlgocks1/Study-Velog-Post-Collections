코틀린을 활용하면 DSL(Domain Specific Language)를 직접 만들 수 있다.
`도메인 특화 언어`라고 불리며 복잡한 객체, 계층 구조를 갖고 있는 객체들을 정의할 때 유용하다.

### 사용자 정의 DSL 만들어 보기

사용자 정의 DSL를 만들기 전에 `리시버를 사용하느 함수 타입`에 대해 알아야 한다.

#### 함수 타입이란?

```
inline fun <T> Iterable<T>.filter(
	predicate: (T) -> Boolean
): List<T> {
    return filterTo(ArrayList<T>(), predicate)
}
```

filter의 함수에서 `predicate` 즉 (T) -> Boolean이 함수 타입이다.

- ()->Unit : 파라미터를 갖지 않고 Unit을 리턴
- (Int) -> Unit - Int를 파라미터로 받고, Unit을 리턴
- (Int) -> () -> Unit : Int를 파라미터로 받으며 다른 함수를 리턴하는 함수이다. 이때 다른 함수는 파라미터를 받지 않고 Unit을 리턴
- (()->Unit) -> Unit : 다른 함수를 파라미터로 받고, Unit을 리턴 이 때 다른 함수는 파라미터로 아무것도 받지 않고 Unit을 리턴

함수 타입을 만드는 기본적인 방법은 다음과 같다.

- 람다 표현식
- 익명 함수
- 함수 레퍼런스

다음과 같은 함수가 있다고 하자,

```
fun plus(a: Int, b: Int) = a + b
```

유사 함수는 다음과 같이 만든다.

```
val plus1: (Int, Int)->Int = { a,b -> a+b }
val plus2: (Int, Int)->Int = fun(a, b) = a+b
val plus3: (Int, Int)->Int = ::plus
```

![](https://velog.velcdn.com/images/cksgodl/post/660208a1-46f3-4c09-b22b-9d57b0275dd2/image.png)

```
    println(plus1) // (kotlin.Int, kotlin.Int) -> kotlin.Int
    println(plus2) // (kotlin.Int, kotlin.Int) -> kotlin.Int
    println(plus2) // (kotlin.Int, kotlin.Int) -> kotlin.Int
    println(plus3(1,2)) // 3
```

함수 타입은 `함수를 나타내는 객체`를 표현하는 타입이다.
`익명 함수`는 일반적인 함수처럼 보이지만, 이름을 가지고 있지 않다.
`람다 표현식`은 익명 함수를 짧게 나타내는 표기 방법이다.

```
val plus4 = ({ a: Int,b: Int -> a+b }) // 익명 함수

val plus1: (Int, Int)->Int = { a,b -> a+b } // 람다 표현식
```

`확장 함수`에서의 익명함수는 일반 함수처럼 만들고 이름만 빼면 된다.

```
fun Int.myPlus(other: Int) = this + other

val myPlus = fun Int.(other: Int) = this + other
```

두번째 myPlus함수의 타입은 어떻게 될까? 확장 함수를 나타내는 특별한 타입이 된다. 이를 `리시버를 가진 함수 타입`이라고 한다. (리시버 == Int)

일반적인 함수 타입과 비슷하지만, 파라미터 앞에 리시버 타입이 추가되어 있어 점(.)기호로 구분되어 있다.

![](https://velog.velcdn.com/images/cksgodl/post/9b99d1c1-8570-4452-a9aa-f5a7d288f067/image.png)

```
val myPlus: Int.(Int)->Int
	= fun Int.(other: Int) = this + other
```

이와 같이 함수는 람다식, 구체적으로 리시버를 가진 람다 표현식을 사용해서 정의할 수 있다. 이렇게하면 스코프 내부에 this 키워드가 확장 리시버를 참조하게 된다.

```
val myPlus: Int.(Int) -> Int = { this + it } // 람다식으로 표현
```

람다표현식은 다음과 같이 호출될 수 있다.

```
myPlus.invoke(1, 2)
myPlus(1, 2)
1.myPlus(2)
```

리시버를 가진 함수 타입의 가장 중요한 점은 `this`의 참조 대상을 변경할 수 있다는 것이다.
this는 apply 함수에서 리시버 객체의 메서드와 프로퍼티를 간단하게 참조할 수 있게 해준다.

```
inline fun <T> T.apply(block: T.() -> Unit): T {
	this.block()
    return this
}
// 제너릭 T에 대한 익명 확장함수 block()을 실행 후 실행한 결과 값을 반환
```

```
data class User(
    var name:String = "",
    var surname: String = ""
)

println(User().apply {
  	name = "해찬"
	surname = "이"
}) // User(name=해찬, surname=이)
```

이러한 리시버를 가진 함수 타입은 코틀린 DSL을 구성하는 가장 기본적인 블록이다.

---

이를 활용해서 HTML 테이블을 표현해보자.

```
fun createTable() = table {
    tr{
        for(i in 1..2) {
            td {
                +"This is colmn $i"
            }
        }
    }
}
```

- `table`이라는 함수가 익명함수(람다 식)을 프로퍼티로 받고 있고 있다.
- tr이라는 함수가 table내부에 정의되어 있다. 즉 table 함수의 파라미터는 tr 함수를 갖는 리시버를 가져야 한다.
- 비슷하게 tr 함수의 파라미터도 td 함수를 갖는 리시버를 가져야 한다.

```
class TdBuilder {
	var text = ""
	operator fun String.unaryPlus() {
        text += this
        // + 연산자를 상속 받아
        // "This is a Coulmn"을 표현한다.
	}
}

class TrBuilder{
    fun td(init: TdBuilder.()->Unit){ // Td를 빌드해주는 람다식을 파라미터로
    	// TODO
    }
}

class TableBuilder {
    fun tr(init: TrBuilder.()->Unit) {
    	// TODO
    }
}
```

`table`함수에서 TableBuilder를 리턴해야하는데

```
fun table(init: TableBuilder.() -> Unit): TableBuilder {
	val tableBuilder = TableBuilder()
    init.invoke(tableBuilder)
    return tableBuidler
}
```

다음과 같은 소스는 apply를 사용하여 짧게 표현할 수 있다.
// block() 람다식을 실행 한 결과(this)를 리턴하기 때문

```
fun table(init: TableBuilder.()->Unit): TableBuilder = TableBuilder().apply(init)
```

또한 Tr, Td는 한 개 이상의 값이 들어올 수 있기에 List로 확장하여 선언하였다.

```
class TrBuilder{
    val tds = mutableListOf<TdBuilder>()
    fun td(init: TdBuilder.()->Unit){
        tds.add(TdBuilder().apply(init))
    }
}

class TableBuilder {
    val trs = mutableListOf<TrBuilder>()
    fun tr(init: TrBuilder.()->Unit) {
        trs.add(TrBuilder().apply(init))
    }
}
```

DSL을 모두 정의하였고, 이러한 DSL이 `toString()`함수를 통해 태그로 출력되기 위해 다음과 같은 클래스를 컴포지션하여 사용하였다.

```
class Tag(val tag: String){
    fun <T> converToString(content: List<out T>): String {
        var text = ""
        content.forEach { text += it }
        return "<$tag>$text</$tag>"
    }
}

class TrBuilder{
    val tds = mutableListOf<TdBuilder>()
    val tag = Tag("tr")

    fun td(init: TdBuilder.()->Unit){
        tds.add(TdBuilder().apply(init))
    }
    override fun toString(): String = tag.converToString(tds) // toString() 오퍼레이터 상속
}
```

전체소스

```
class Tag(val tag: String){
    fun <T> converToString(content: List<out T>): String {
        var text = ""
        content.forEach { text += it }
        return "<$tag>$text</$tag>"
    }
}

class TdBuilder {
    var text = ""
    val tag = Tag("td")
    operator fun String.unaryPlus() {
        text += this
    }
    override fun toString(): String = tag.converToString(listOf(text))
}

class TrBuilder{
    val tds = mutableListOf<TdBuilder>()
    val tag = Tag("tr")

    fun td(init: TdBuilder.()->Unit){
        tds.add(TdBuilder().apply(init))
    }
    override fun toString(): String = tag.converToString(tds)
}

class TableBuilder {
    val trs = mutableListOf<TrBuilder>()
    val tag = Tag("table")

    fun tr(init: TrBuilder.()->Unit) {
        trs.add(TrBuilder().apply(init))
    }
    override fun toString(): String =tag.converToString(trs)
}

// 리시버(TableBuilder)를 가진 함수 타입
fun table(init: TableBuilder.()->Unit): TableBuilder = TableBuilder().apply(init)

fun createTable() = table {
    tr{
        for(i in 1..2) {
            td {
                +"This is colmn $i"
            }
        }
    }
}


fun main() {
    println(createTable().toString())
    // <table><tr><td>This is colmn 1</td><td>This is colmn 2</td></tr></table>
}
```

### 언제 DSL을 사용해야 할까

DSL의 구현은 해당 DSL이 익숙하지 않는 개발자에게 혼란과 어려움을 줄 수도 있다. 또한 좋은 DSL을 만드는 작업도 굉장히 힘들다.

그러므로

- 복잡한 자료 구조
- 계층적인 구조
- 거대한 양의 데이터

등 의 예시에서만 활용하는 것이 좋다.

참고 자료

https://taes-k.github.io/2021/09/22/kotlin-dsl/
