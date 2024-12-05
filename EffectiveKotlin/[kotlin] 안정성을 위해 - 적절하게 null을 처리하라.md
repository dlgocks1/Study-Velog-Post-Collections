> null : 값이 부족하다(lack of value)

프로퍼티의 값이 null이라는 것은 값이 설정되어 있지 않거나, 제거되어있다는 것을 의미한다. 

null은 최대한 명확한 의미를 가지고 사용되어야 하고, 개발자는 이에 따라 적절하게 nullable 값을 처리해야 한다.

```
val printer: Printer? = getPrinter()
printer.print() // 컴파일 오류

printer?.print() // 안전 호출
if (printer != null) printer.print() // 스마트 캐스팅
printer!!.print() // non-null assertion
```

기본적으로 nullable타입은 세 가지 방법으로 처리한다.

* `안전호출(?.)`, `스마트 캐스팅`, `Elvis 연산자(?:)` 등을 활용하여 안전하게 처리
* 오류를 throw한다.
* 함수 또는 프로퍼티를 리팩터링하여 nullable 타입이 나오지 않게 바꾼다.


#### 안전호출과 스마트 캐스팅
null을 안전하게 처리하는 방법 중 널리 사용되는 방법들이다.

```
printer?.print() // 안전 호출
if (printer != null) printer.print() // 스마트 캐스팅

printer?.let{
	// let을 null체크에 사용하지 말기 
    it.print()
}
```
[let을 null체크에 사용하지 말기](https://velog.io/@cksgodl/kotlin-%EC%95%88%EC%A0%95%EC%84%B1%EC%9D%84-%EC%9C%84%ED%95%B4-%EC%B6%94%EB%A1%A0inferred-%ED%83%80%EC%9E%85%EC%9C%BC%EB%A1%9C-%EB%A6%AC%ED%84%B4%ED%95%98%EC%A7%80-%EB%A7%90%EB%9D%BC-%EC%98%88%EC%99%B8%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%B4-%EC%BD%94%EB%93%9C%EC%97%90-%EC%A0%9C%ED%95%9C%EC%9D%84-%EA%B1%B8%EC%96%B4%EB%9D%BC)

위 코드 모두 printer가 null이 아닐 때 print()를 호출한다.

#### Elvis 연산자 (:?)
```
val printerName1 = printer?.name ?: "Unnamed"
val printerName2 = printer?.name ?: return
val printerName3 = printer?.name ?: 
	throw Error("Printer must be named")
```

많은 객체가 nullable과 관련된 처리를 지원한다. Kotlin의 컬렉션 처리를 할 때에는 무언가 없다는 것을 나타낼 때는 null이 아닌 빈 컬렉션을 사용하는 것이 일반적이다.

> It is considered a best practice to NEVER return null when returning a collection or enumerable. ALWAYS return an empty enumerable/collection. It prevents the aforementioned nonsense, and prevents your car getting egged by co-workers and users of your classes.

배열이나 컬렉션을 반환할 때 null을 반환하지 않는 것이 가장 좋은 방법으로 간주된다. **항상 비어있는 컬렉션을 반환해야 한다.** 
~~당신의 차가 당신의 동료들과 당신의 수업의 사용자들에 의해 계란 범벅이 되는것을 막아준다고 한다.~~

다음과 같은 확장 함수 또는 emptyList()와 같은 함수를 이용해 빈 컬렉션을 반환하자.
```
Collection<T>?.orEmpty()
emptyList()
emptySet()
emptyFlow() 
PagingData.empty() // Collection이 아니더라도 API에서 Empty값을 지원하는 경우가 많다.
...
```

### 방어적 프로그래밍과 공격적 프로그래밍

모든 가능성을 올바른 형식으로 처리하는 것(ex null일 때는 출력하지 않기)을 **방어적 프로그래밍**이라고 한다. 코드가 프로덕셚 ㅘㄴ경으로 들어갔을 때 발생할 수 있는 수많은 것들로 부터 프로그램의 안전성을 높여준다.

모든 상황을 안전하게 처리하는 것은 불가능하다. 이러한 경우에는 **공격적프로그래밍**을 사용한다. 예상치 못한 상황이 발생했을 때 require, check, assert와 같은 함수를 이용해 오류를 발생시켜 개발자에게 수정하게 만든다. 

### 오류를 throw하기

throw 및 require, check, assert를 이용해 오류를 강제로 발생시키자.
[예외를 활용해 코드에 제한을 걸자](https://velog.io/@cksgodl/kotlin-%EC%95%88%EC%A0%95%EC%84%B1%EC%9D%84-%EC%9C%84%ED%95%B4-%EC%B6%94%EB%A1%A0inferred-%ED%83%80%EC%9E%85%EC%9C%BC%EB%A1%9C-%EB%A6%AC%ED%84%B4%ED%95%98%EC%A7%80-%EB%A7%90%EB%9D%BC-%EC%98%88%EC%99%B8%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%B4-%EC%BD%94%EB%93%9C%EC%97%90-%EC%A0%9C%ED%95%9C%EC%9D%84-%EA%B1%B8%EC%96%B4%EB%9D%BC#%EC%95%84%EA%B7%9C%EB%A8%BC%ED%8A%B8-require)
```
fun process(user: User){
	requireNotNull(user.name) // require 아규먼트
    val context = checkNotNull(context) // check 상태
    val networkService = 
    	getNetworkService(context) ?:
        throw NoInternetConnection()
    networkService.getData { data, userData ->
    	show(deta!!, userData!!)
    }
}
```

### not-null assertion(`!!`)에 대하여

nullable을 가장 간단하게 처리하는 방법은 not-null assertion(`!!`)을 사용하는 것이다. 그러나 null인 값에 잘못 참조하면 NPE 오류가 발생한다.

`!!`은 사용하기 쉽지만 좋은 해결방법은 아니다. 예외가 발생할 때, 어떤 설명도 없는 제네릭 예외(generic exception)이 발생하며, 코드가 짧고 쉽다 보니 남용하는 경우도 많다. 

nullability(null일 수 있는지)와 관련된 정보는 숨겨져 있으므로, 굉장히 쉽게 놓칠 수 있다. 변수를 일단 선언하고 이후에 사용하기 전에 값을 할당해서 사용하기로 하고, 다음과 같은 코드를 작성했다고 해 보자.
```
class UserControllerTest {
	private var dao: UserDao? = null
    private var controller: UserContoller? = null
    
    @BeforeEach
    fun init(){
    	dao = mockk()
        controller = UserController(dao!!)
    }
    
    @Test
    fun test(){
    	controller!!.doSomething()
    }
}
```
변수를 초기에 null로 설정하고 이후에 `!!`연산자를 사용하는 방법은 좋은 처리 방법이 아니다.
이렇게 처리한다면 변수를 나중에 계속 언팩(unpack)해야 함으로 사용하기 귀찮으며, 이후 의미 있는 null값을 가질 가능성 자체를 차단해 버린다.
> lateinit 또는 Delegates.notNull을 사용하자.

### 의미 없는 nullability 피하기

nullable한 변수에 대해서는 어떻게든 적절하게 처리가 필요함으로 추가 비용이 발생한다. 따라서 필요한 경우가 아니라면, nullability자체를 피하는 것이 좋다. 다른 개발자가 보기에 의미가 없을 때는 null을 사용하지 않는 것이 좋다. 특별한 이유 없이 null을 사용한다면 `!!`를 사용하게 되기 때문

* `List<T>`의 get과 getOrNull과 같은 함수를 만들어서 제공하자.

* lateinit 프로퍼티와 notNUll 델리게이트를 사용하여 null로 초기화 하는 것보다는 초기화를 지연하자.

* 빈 컬렉션 대신 null을 리턴하지 말자. `List<Int>?`와 `List<Int?>`는 의미가 완전히 다르다. 컬렉션의 요소가 없다는 것을 나타낼 때는 빈 컬렉션을 사용하자.

* nullable enum과 None enum 값은 완전히 다른 의미이다. null enum은 별도로 처리해야 하지만, None enum 정의에 없으므로 필요한 경우에 사용하는 쪽에서 추가로 활용할 수 있다.

### lateinit 프로퍼티와 notNull 델리게이트

클래스 생성 중에 초기화 할 수 없는 프로퍼티를 가지는 것은 드문 일이지만, 분명 존재하는 일이다. 이러한 프로퍼티는 사용 전에 반드시 초기화해서 사용해야 한다.

JUnit의 @BeforeEach처럼 다른 함수들보다도 먼저 호출되는 함수에서 프로퍼티가 설정되는 경우가 있다.

프로퍼티를 사용할 때마다 nullable에서 null이 아닌 것으로 타입변환 하는것은 바람직하지 않다. lateinit 한정자를 사용하여 이를 효율적으로 바꾸어보자.

```
class UserControllerTest {
	private lateinit var dao: UserDao = null
    private lateinit var controller: UserContoller = null
    
    @BeforeEach
    fun init(){
    	dao = mockk()
        controller = UserController(dao)
    }
    
    @Test
    fun test(){
    	controller.doSomething()
    }
}
```
lateinit을 사용할 경우에도 비용은 발생한다. 또한 초기화 전에 값을 사용하려고 한다면 예외가 발생한다.
* `!!`연산자로 연팩하지 않아도 된다.
* 이후에 의미있는 null을 사용하고 싶을 때, nullable로 만들 수 있다.
* 프로퍼티가 초기화 된 이후에는 초기화되지 않은 상태로 돌아갈 수 없다.

lateinit를 사용할 수 없는 경우도 있는데, JVM에서 Int, Long, Double, BOolean과 같은 기본타입과 연결된 타입으로 프로퍼티를 연결해야 하는 경우이다.
이러한 경우에는 Delegates.notNull을 사용한다.

```
private var userId: Int by Delegates.notNull()
private var isChecking: Boolean by Delegates.notNull()
```

lateinit이 아니라 프로퍼티 위임을 이용해 초기화를 지연할 수 있다.








참고 자료 

https://stackoverflow.com/questions/1969993/is-it-better-to-return-null-or-empty-collection

