코틀린의 Any클래스에는 다음과 같이 잘 설정된 규약들을 가진 메서드들이 있다.

* equlas
* hashCode
* toString

이러한 메소드들의 규약은 주석과 문서에 잘 저장되어 있다.
Any 클래스를 상속받는 모든 메소드들은 이러한 규약을 잘 지켜주는 것이 좋다. 해당 메소드들은 자바 때부터 정의되어 있던 메소드라서 코틀린에서 중요한 위치를 차지하고 있으며, 수많은 객체와 함수들이 이 규약에 의존하고 있다.


## 동등성(equlas)

코틀린에는 두 가지 종류의 동등성이 있다.

* 구조적 동등성 : equals 메소드를 기반으로 만들어진 `==`연산자로 확인하는 동등성이다. a가 nullable이 아니라면 `a == b`는 `a.equlas(b)`로 변환되고, a가 nullable이라면 `a?.equlas(b) ? : (b === null)`로 변환 된다. 

* 레퍼런스적 동등성 : `===`연산자로 확인하는 동등성으로 두 핀연산자가 같은 객체를 가리키면, true를 반환한다.

이런 equals는 모든 클래스의 슈퍼클래스인 Any에 구현되어 있으므로, 모든 객체에서 사용할 수 있다.

### 동등성이 필요한 이유

Any클래스에 구현되어 있는 equals 메서드는 디폴트로 ===처럼 두 인스턴스가 완전히 같은 객체인지를 비교한다. 이는 모든 객체는 디폴트로 유일한 객체라는 것을 의미한다.

```
class Name(val name: String)
val name1 = Name("marcin")
val name2 = Name("marcin")
val name1Ref = name1

name1 == name1 // true
name1 == name2 // false
name1 == name1Ref // true

name1 === name1 // true
name1 === name2 // false
name1 === name1Ref // true
```

> [[Kotlin] 데이터의 집합 표현에 data class를 사용하라](https://velog.io/@cksgodl/Kotlin-%EB%8D%B0%EC%9D%B4%ED%84%B0%EC%9D%98-%EC%A7%91%ED%95%A9-%ED%91%9C%ED%98%84%EC%97%90-data-class%EB%A5%BC-%EC%82%AC%EC%9A%A9%ED%95%98%EB%9D%BC)
`data class`는 객체가 다르더라도 데이터 클래스내의 프로퍼티가 같으면 같은 해쉬코드값을 반환한다.

### equals을 새로 구현해야 할 때

* 동등성을 확인할 때 검사되지 않는 프로퍼티가 존재할 때 (일부 프로퍼티만 비교해야할 경우)

유저의 아이디만 같으면 같은 객체라고 판단하고 싶을 때
```
class User(
    val id : Int,
    val name : String,
    val nickName : String
){
    override fun equals(other: Any?): Boolean {
        return other is User && other.id == id
    }
}
```

* data 한정자를 붙이는 것을 원하지 않거나, 비교해야 하는 프로퍼티가 기본 생성자에 없는 경우

유저의 id와 name을 통한 이중해싱 해쉬코드를 비교할 때
```
class User(
    val id : Int,
    val name : String,
    val nickName : String
){
    private var userHashCode : Int = (id.hashCode() + name.hashCode()).hashCode()
    
    override fun equals(other: Any?): Boolean {
        return other is User && other.userHashCode == userHashCode
    }
}
```

### equals 규약

* 반사적 동작 : `x`가 `null`이 아니라면 `x.equals(x)`는 true이다.

* 대칭적 동작 : `x`와 `y`가 널이 아닌 값이라면, `x.equals(y)`는 `y.equals(x)`와 동일해야 한다.

* 연속적 동작 : `x`, `y`, `z`가 널이 아니고, `x.equals(y)`와 `y.equals(z)`는 `x.equals(z)`와 동일해야한다.

* 일관적 동작 : `x`, `y`가 널이 아니고, `x.equals(y)`는 여러번 실행해도 동일한 값이여야 한다.

* 널과 관련된 동작 : `x`가 널이 아니라면 `x.equals(null)`은 항상 `false`이다.

>추가적으로 `equals`, `toString`, `hashCode`의 동작은 빠르게 동작해야 한다.(빠르게 동작하는 것을 예상하고 있기에)


### 동작 위반사례

```
class Time(
    val milliArg: Long = -1,
    val isNow: Boolean = false
) {
    val millis: Long
        get() = if (isNow) System.currentTimeMillis() else milliArg

    override fun equals(other: Any?): Boolean {
        return other is Time && millis == other.millis
    }
}

fun main() {
    val now = Time(isNow = true)
    println(List(1000000) { now }.all {it == now }) // false
}
```
해당 코드는 실행될 때 마다 달라질 수있기에 일관적 동작도 위반하며, `x.equlas(x) == true`도 위반할 수 있다.

> **다른 클래스를 동등하게 만들지 말자**

1과 1.0은 다르며, 1.0과 1.0F도 다르다. 이들은 타입이 다르므로 비교 자체가 안된다. 

예를들어 다음과 같은 예를 보자

```
interface Customber{
    val id: Int
    val name : String
}

open class ACustomber(
    override val id : Int,
    override val name : String,
) : Customber {
    override fun equals(other: Any?): Boolean {
        return when(other){
            is ACustomber -> id == other.id
            is BCustomber -> name == other.name
            else -> false
        }
    }
}

class BCustomber(
    override val id : Int,
    override val name : String,
    val nickName: String = "팔코",
) : ACustomber {
    override fun equals(other: Any?): Boolean {
        return when(other){
            is ACustomber ->
                (id.toString() + name).hashCode() == (other.id.toString() + other.name).hashCode()
            is BCustomber -> nickname == other.nickname
            else -> false
        }
    }
}

fun main() {
    val customer1 = BCustomber(1,"해찬","팔코")
    val customer2 = ACustomber(1,"해찬")
    val customer3 = BCustomber(1,"해찬","스무디블루")

    println(customer1.equals(customer2)) // true
    println(customer2.equals(customer3)) // true
    println(customer1.equals(customer3)) // false
}
```
A와 B고객 둘다 Customer을 상속받고 있으며

A고객의 동등성 체크는 다음과 같다.
* A고객에 대해 id값이 같은지
* B고객에 대해 name이 같은지

B고객의 동등성 체크
* A고객에 대해 id와 name을 더한 값의 해쉬코드가 같은지
* B고객에 대해 닉네임이 같은지

다음과 같은 예는 연속적 동작 (`x==y, y==z, x==z`)를 위반한다.

A와 B의 동등성 중 한쪽을 수정할 수 없을 때 다음과 같은 상황은 매우 난감하게 된다. 
그럼으로 **다른 클래스를 동등하게 만들지 말자**

하지만! 현재 A고객과 B고객은 상속 관계를 가지므로 같은 객체를 비교하게 만드는 것은 좋지 않은 선택이다. 이렇게 구현하면 리스코프 치환 원칙을 위반하기 때문이다. (더욱 사용하면 안되는 선택지) 따라서 상속대신 컴포지션을 사용하고, 두객체를 아예 비교하지 못하게 만드는 것이 좋다.

코드로 구현하면 다음과 같다.

```
data class ACustomber(
    val id : Int,
    val name : String,
)

data class BCustomber(
    val aCustomber: ACustomber,
    val nickName: String = "팔코",
)

fun main() {
    val customer1 = BCustomber(ACustomber(1,"해찬"),"팔코")
    val customer2 = ACustomber(1,"해찬")
    val customer3 = BCustomber(ACustomber(1,"해찬"),"스무디블루")

    println(customer1.aCustomber == customer2) // true
    println(customer2 == customer3.aCustomber) // true
    println(customer1.aCustomber == customer3.aCustomber) // true

    println(customer1 == customer2) // 컴파일 에러 객체 비교 불가
    println(customer2 == customer3) // 컴파일 에러 객체 비교 불가
    println(customer1 == customer3) // false
}
```

동등성은 반드시 일관성을 가져야 한다. 두 객체를 비교한 결과는 한 객체를 수정하지 않는 한 항상 같은 결과를 내야한다.

### URL에 관련된 equals문제

equals를 잘못 설계한 예로는 java.net.URL이 있다.
이는 객체 2개를 비교할 때 같은 IP주소로 해석될 때는 true, 아니면 false가 나온다. 하지만 이 상태는 네트워크 상태에 따라서 달라진다. 다음예를 보자.

```

import java.net.URL

fun main() {
    val enWiki = URL("https://en.wikipedia.org/")
    val wiki = URL("https://wikipedia.org/")

    println(enWiki == wiki) 
}
```

인터넷이 연결되어 있으면 true를 출력하지만, 연결되어 있지 않으면, false를 출력한다. 이는 동등성이 네트워크에 의존하고 있음을 의미한다.

또한 네트워크 요청이 들어가기 때문에 빠를거라고 예상되는 `equals`는 느리게 작동된다. 안드로이드 같은 경우는 기본 쓰레드에서 네트워크 작업은 금지된다. 이런 환경에서는 URL을 `set`에 추가하는 것도, 기본적인 조작도 쓰레드를 나누어 해야한다.

동작 자체도 문제가 있다. 가상 호스팅을 사용한다면 다른 사이트가 같은 IP 주소를 공유할 수도 있다.

> 가상 호스팅이란?

하나의 서버에 여러 도메인을 등록하여 IP는 같지만 각각의 도메인마다 다른 홈페이지를 제공해 주는 것

![](https://velog.velcdn.com/images/cksgodl/post/1d369454-8970-432a-aef2-9ffd4d0416de/image.png)

이러한 문제를 해결하기 위해 `Android 4.0`부터는 호스트 이름이 동일할 때만 true를 리턴하며, `코틀린/JVM` 또는 다른 플랫폼을 사용할 때는 `java.net.URI`를 사용한다.

### equals을 직접구현하는 것은 좋지 않다.

특별한 이유가 없는 이상, 직접 `equals`를 구현하는 것은 좋지 않다. 제공되는 것을 그대로 쓰거나 data class를 사용하자.
그래도 직접 구현해야 한다면, 반사적, 대칭적, 연속적, 일고나적 등의 동작을 꼭 준수하는지 확인하자. 또한 final 클래스로 만들어 서브 클래스에서 `equals`에 대한 수정이 불가능하게 만들어야 한다.

---


# hashCode의 규약을 지켜라.

hashcode는 자료 구조인 해시 테이블(hash table)을 구축할 때 사용된다.

## 해시 테이블

해시테이블이 왜 만들어 졌을까? 컬렉션에 요소를 빠르게 추가하고, 요소를 빠르게 추출해야 한다고 해보자. 요소가 포함되어 있는지 확인할 때 하나하나 모든 요소와 비교해야 한다. 수백 만개의 요소가 들어간 배열에서 이를 수행한다는 것은 쉽지 않을 것이다. 그럼으로 배열 또는 링크드 리스트를 기반으로 만들어진 컬렉션은 요소가 포함되어있는지 확인하는 성능이 좋지 않다.  

그래서 만든 것이 해시 테이블이다. 해시 테이블은 각 요소에 숫자를 할당하는 함수가 필요하다. 이 함수를 해시 함수라고 부르며, 같은 요소라면 항상 같은 숫자를 리턴한다. 해시 함수가 다음과 같은 특성을 갖고 있으면 좋다.

* 속도가 빠를 것
* 충돌이 적을 것

해시 함수는 요소를 해쉬코드로 바꾼 후 해쉬코드에 따른 버킷에 넣는다. 버킷은 배열처럼 구성되며 요소를 찾을 때도 해시코드에 따른 버킷에 있는 내용만 확인하면 된다.

![](https://velog.velcdn.com/images/cksgodl/post/071a309f-08f7-4a34-ac26-c86b6d622a06/image.png)

해시 테이블의 개념은 코틀린/JVM의 기본 셋(LinkedHashSet)과 기본 맵(LinkedHashMap)에도 사용된다. 해쉬코드를 만들 때는 `hashCode()`함수를 사용한다. 

> 일반적으로 ahsCode 함수는 Int를 리턴함으로 해시 버킷은 4,294,967,294 약 40만개가 만들어 지는데 이는 한두 개의 요소만 포함할 셋으로는 큰 크기다. 기본적으로 숫자를 더 작게 만드는 변환을 사용하다가, 필요한 경우 변환 방법을 바꾸어 해시 테이블을 크게 만든다고 한다.

### 가변성과 관련된 문제

요소가 추가될 때만 해시 코드를 계산한다. 요소가 변경되어도 해시 코드는 계산되지 않으며 재배치도 이루어지지 않습니다. 그래서 기본적인 `LinkedHashSet`과 `LinkedHasMap`의 키는 한 번 추가한 요소를 변경할 수 없다.

```
data class Fullname(
    var firstName: String,
    var lastName: String,
)

fun main() {
    val name = Fullname("이","해찬")
    val mutableSet =  mutableSetOf<Fullname>()
    mutableSet.add(name)
    name.firstName = "김"
    println(name) // Fullname(firstName=김, lastName=해찬)
    println(name in mutableSet) // false
    println(mutableSet.first() == name) // true mutableSet이 첫 번째로 가르키는 버킷에 있는 내용은 변하지 않음 
}
```
해시 등의 `mutable`프로퍼티로 요소를 조합하는 자료 구조에서는 `mutable`객체가 활용되면 안되며 사용하더라도 요소를 변경해서는 안된다. (`firstName`, `lastName`도 mutable하고, `MutableSet`도 mutable하기 때문) 이러한 이유로 `immutable`객체를 많이 사용한다.

### hashCode 규약

* 어떤 객체를 변경하지 않았다면 hasCode는 여러 번 호출해도 동일한 결과여야 한다.
* equals 메서드의 실행결과로 두 객체가 같다고 나오면, hashCode 메서드도 동일해야 한다.
`equals`와 `hashCode`는 일관된 동작을 수행해야 한다.

그래서 코틀린은 equals 구현을 오버라이드할 때, hashCode도 함께 오버라이드하는 것을 경고한다.

![](https://velog.velcdn.com/images/cksgodl/post/c0073737-e922-40ef-bf37-3541ba780639/image.png)

만약 해쉬코드를 직접 구현한다고 하면 해쉬코드를 최대한 넓게 퍼트려야 한다. 중복이 많으면 입력, 추출 모두 다 오래걸리기 때문이다.


# compareTo의 규약을 지켜라

compareTo는 Any 클래스에 있는 메서드가 아니다. 이는 수학적인 부등식으로 변환되는 연산자이다.
```
obj1 > obj2 // obj1.compareTo(obj2) > 0
obj1 < obj2 // obj1.compareTo(obj2) < 0
obj1 >= obj2 // obj1.compareTo(obj2) >= 0
obj1 <= obj2 // obj1.compareTo(obj2) <= 0
```

compareTo 메서드는 `Comparable<T>` 인터페이스에도 들어있다. 어떤 객체가 compareTo 메서드를 갖고 있다는 의미는 해당 객체가 어떤 순서를 갖고 있으므로, 비교할 수 있다는 것입니다. 

compareTo는 다음과 같이 동작해야 한다.

* 비대칭적 동작 : `a >= b` 이고 `b >= a` 라면, `b == a`여야 한다.

* 연속적 동작 : `a >= b` 이고 `b >= c` 이면, `a >= c`여야 한다.

* 코넥스적 동작: 두 요소는 확실한 관계를 가지고 있어야 한다. 즉, `a >= b`또는 `b >= a`중에 적어도 하나는 `true`를 반환해야 한다.

### compareTo를 따로 정의해야 할까?

코틀린에서 따로 `compareTo`를 구현하는 경우는 거의 없다. 일반적으로 하나를 기반으로 순서를 지정하는 것으로 충분하기 때문이다.

예를 들어 `sortedBy`를 사용하면 원하는 키로 컬렉션을 정렬할 수 있다.
```
val names = listOf<Fullname>( /* .. */ )
val sorted = names.sortedBy { it.firstName }
```

여러 프로퍼티를 기반으로 정렬하기 원한다면 `sortedWith`를 사용하면 된다. 이 함수는 `compareBy`를 활용해 비교기를 만들어 사용한다. 다음 코드는 `firstName`으로 정렬 한 후, `lastName`으로 정렬하는 코드이다.

```
val names = listOf<Fullname>(Fullname("이", "해찬"), Fullname("김", "해찬"), Fullname("강", "해찬"))
val sorted = names.sortedWith(compareBy({ it.firstName }, { it.lastName }))
println(sorted)
```

`Fullname`에 대한 `Comparable<Fullname>`를 구현하는 형태로도 만들 수 있다.

문자열과 알파벳은 순서가 있다. 따라서 내부적으로 `Comparable<String>`을 구현하고 있다. 텍스트는 일반적으로 알파벳과 숫자 순서로 정렬해야 하는 경우가 많으므로 굉장히 유용하다. 하지만 단점도 있다.
직관적이지 않은 부등호를 기반으로 두 문자열을 비교하는 코드는 이해하는데 시간이 걸린다.
```
"Kotlin" > "Java" // true
```

객체마다 자연스러운 정렬순서를 선언하고 이를 companion 객체로 만들어 두는 것이 좋다.

```
data class Fullname(
    var firstName: String,
    val lastName: String,
) {
    companion object {
        val DISPLAY_ORDER = compareBy<Fullname>({ it.firstName }, { it.lastName })
    }
}

val sorted = names.sortedWith(DISPLAY_ORDER)
```

### 직접 compareTo 구현하기

compareTo를 단순 구현할 때 유용하게 활용할 수 있는 톱레벨 함수가 있다. 두 값을 단순하게 비교만 한다면 `compareValues`함수를 활용하면 된다.

```
data class Fullname(
    var firstName: String,
    val lastName: String,
) : Comparable<Fullname> {

    override fun compareTo(other: Fullname): Int {
        return compareValues(firstName, other.firstName)
    }
}
```

더 많은 값을 비교하거나, selector을 활용해서 비교하고 싶다면, 다음과 같이 `compareValuesBy`를 사용한다.

```
data class Fullname(
    var firstName: String,
    val lastName: String,
) : Comparable<Fullname> {

    override fun compareTo(other: Fullname): Int {
        return compareValuesBy(this, other, { it.firstName }, { it.firstName })
    }
}
```
* 0 : 리시버와 other이 동일한 경우
* 양수 : 리시버가 other보다 큰 경우
* 음수 : 리시버가 other보다 작은 경우

이 함수는 비교기를 만들 때 도움이 된다. 비교기를 구현한 뒤에는 비대칭적 동작, 연속적 동작, 코넥스적 동작을 만족하는지 확인하자.

