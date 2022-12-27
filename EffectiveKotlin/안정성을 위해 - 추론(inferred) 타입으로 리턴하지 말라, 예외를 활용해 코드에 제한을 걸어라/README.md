## 추론 타입으로 리턴하지 말라

kotlin의 타입추론은 할당 될 때의 정확하게 오른쪽에 있는 피연산자에 맞게 설정된다.

다음과 같은 예를 보자.

```
open class Animal
class Zebra: Animal()

fun main() {
	var animal = Zebra()
    animal = Animal() // 오류 : Type Mismatch
}
```

이경우 animal이 Zebra 타입으로 정의되어 상위클래스인 Animal을 설정하여도 오류가 남을 볼 수 있다.

절대로 슈퍼클래스 또는 인터페이스로는 설정되지 않는다.

```
fun main() {
	var animal : Animal = Zebra()
    animal = Animal() // Possible!
}
```

원하는 타입의 상위 타입을 명시적으로 지정하여 사용하면 이러한 문제는 해결된다.

타입을 명확하게 지정해야 하는 경우에는 명시적으로 타입을 지정해야 한다는 원칙을 가지고 진행하자. 추론타입은 프로젝트가 진전될 때, 제한이 너무 많아지거나 예측하지 못한 결과를 낼 수 있다는 것을 기억하자.

## 예외를 활용해 코드에 제한을 걸어라

> 확실하게 어떠한 경우에도 동작해야 하는 코드가 있다면 예외를 활용해 보자.

코드 동작에 제한을 거는 방법으로는 다음과 같은 방법이 있다.

- require 블록 : 아규먼트를 제한할 수 있다.
- check 블록 : 상태와 관련된 동작을 제한할 수 있다.
- assert 블록 : 어떤 것이 true인지 확인할 수 있다. ( 테스트모드에서만 작동 )
- return 또는 throw와 함께 활용하는 Elvis 연산자

이렇게 제한을 걸어서 다른 개발자도 문제를 확인할 수 있다.
문제가 있을경우 예외를 throw해준다. 예상치 못한 동작을 하는 것보다, 예외를 throw하는 것이 문제를 놓치지 않을 수 있고, 코드가 더 안정적으로 작동하게 한다.

### 아규먼트 Require

함수를 정의할 때 타입 시스템을 활용해서 아규먼트에 제한을 걸자.

다음과 같은 예제를 보자

```
fun factorial(n : Int){
	require(n >=0)
    return if (n<=1) 1 else factorial(n-1) * n
}
```

입력의 유효성 검사는 코드의 함수 가장 앞부분에 배치하고, 읽는 사람도 쉽게 확인할 수 있게 하자.

조건을 만족하지 못한다면 IllegalArgument Exception을 발생시킨다.

다음과 같이 람다를 활용하여 지연 메시지를 정의할 수도 있다.

```
fun factorial(n : Int){
	require(n >=0){
    	"0보다 작은 수로는 팩토리얼을 연산할 수 없습니다."
    }
    return if (n<=1) 1 else factorial(n-1) * n
}
```

### 상태 Check

구체적인 조건을 만족할 때만 함수를 사용할 수 있게 해야 할 때가 있다.
다음과 같은 경우를 보자.

- 어떤 객체가 미리 초기화되어 있어야만 처리를 하게 하고 싶은 함수
- 사용자가 로그인했을 때만, 처리를 하게 하고 싶은 함수
- 객체를 사용할 수 있는 시점에 사용하고 싶은 함수

사용 예제를 보자.

```
fun speak(text: String){
	check(isInitiallized)
    // ...
}

fun getUserInfo(): UserInfo{
	checkNotNull(token)
    // ...
}

fun next(): T{
	check(isOpen)
    // ...
}
```

check 함수는 require과 비슷하지만, 지정된 예측을 만족하지 못할 때, IllegalStateException을 throw한다.

### Assert 계열 함수 사용

Assert 계열 함수는 테스트를 할 떄만 활성화 된다. 단위 테스트의 갯수를 줄이거나 간략화 해줄 수 있으며 다음과 같은 장점이 있다.

- Assert 계열의 함수는 코드를 자체 점검하며, 더 효율적으로 테스트를 진행해준다.
- 특정 상항이 아닌 모든 상황에 대한 테스트를 할 수 있다.
- 실행 시점에 정확하게 어떻게 되는지 확인할 수 있다.
- 실제 코드가 더 빠른 시점에 실패하게 만든다. 예상하지 못한 동작이 언제 실행되었는지 찾을 수 있다.

### Nullability와 스마트 캐스팅

코틀린은 require과 check 블록으로 어떤 조건을 확인해서 true가 나왔다면 해당 조건은 이후로도 true일 것이라 판단하고 스마트 캐스팅을 진행한다.

```
public inline fun require(value : Boolean): Unit{
	contract{
    	returns() implies value
	}
    require(value) { "Failed requirement."}
}
```

이러한 특징은 어떤 대상이 null인지 확인할 때 유용하다.

```
class Person(val email: String?)

fun sendEmail(person: Person, message: String){
	require(person.email != null)
    val email: String = person.email
    // ...
}
```

null 체크를 진행할 경우 `requireNotNull`, `CheckNotNull`이라는 특수 함수를 사용해도 괜찮다. 둘 다 스마트 캐스트를 지원함으로, 변수를 언팩하는 용도로 활용할 수 있다.

또한 nullability를 목적으로 오른쪽에 throw 또는 return을 두고 Elvis 연산자를 활용하는 경우도 많다. 이러한 코드는 보기좋고, 읽기 좋고, 유연하게 사용할 수 있다.

오른쪽에 return을 넣으면 오류를 발생시키지 않고 단순하게 함수를 중지할 수 있다.

또는 run 함수를 조합하여 로그를 출력할 수도 있다.

```
fun sendEmail(person: Person, text : String){
	val email: String = person.email ?: return
}

// Activities
context ?: return binding.root

fun sendEmail(person: Person, text : String){
	val email: String = person.email ?: run{
    	log("이메일이 보내지지 않았습니다. 이메일 주소가 없어요")
    	return
    }
    // ...
}
```

## let을 활용하여 null Safe 체크를 하지 마세요?

지금까지 let을 사용하여 null safe 처리를 진행하였는데,

```
    text?.let {
      view.text = it.toString()
    }
```

이러한 코드들이 허용될 수 있으나, 언제나 올바른 let의 사용법은 아니라고 한다.

다음과 같은 예를 보자

```
fun process(str: String?) {
    str?.let { /*Do something*/   }
}
```

이러한 process 함수를 자바로 디컴파일을 진행하면 다음과 같은 형태가 된다.

```
public final void process(@Nullable String str) {
   if (str != null) {
      boolean var4 = false;
      /*Do something*/
   }
}
```

쓸대 없이 추가 변수가 늘었고, 이러한 작업이 많이 수행되면 아무 이득없이 추가적인 작업만 더 하는 코드가 된다.

null 체크를 진행할 때에는 다음과 같이 진행하도록 하자

```
   if (str != null) {
      /*Do something*/
   }

   str ?: {
    // /* Do something */
   } ()
```

참고 자료
출처: https://tourspace.tistory.com/208 [투덜이의 리얼 블로그:티스토리]

### 정리

- require : 아규먼트와 관련된 예측을 정의할 때 사용하는 범용적인 방법
- check : 상태와 관련된 예측을 정의할 때 사용하는 범용적인 방법
- assert : 테스트 모드에서 테스트를 할 때 사용하는 범용적인 방법
- return과 throw와 함꼐 Elvis 연산자 활용하기
