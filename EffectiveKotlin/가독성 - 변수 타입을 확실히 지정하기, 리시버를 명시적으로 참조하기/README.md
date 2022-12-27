### Unit?을 리턴하지 말라

Unit?형은 null 또는 Unit을 가질 수 있다.
True와 False를 가지는 Boolean과 비교해 서로 바꿔서 사용할 수 있다.

일반적으로 Unit?을 사용하는 것은 이런 경우이다.

```
// Boolean
fun keyIsCorrect(key: String): Boolean = //...

if(!keyIsCorrect(key)) return

// Unit?
fun verifyKey(key: String): Unit? = //..

verifyKey(key) ?: return
```

Unit?을 반환값으로 가지는 함수는 멋지고 창의적으로 보일 수도 있지만, 읽을 때는 그렇지 않다. 이는 다른 개발자가 소스를 볼 때 오해의 소지를 남기며, 예측하기 어려운 오류를 남길 수 있다.

따라서 Boolean을 사용하는 형태로 변경하여 사용하자.

### 변수 타입이 명확하지 않은 경우 확실하게 지정하라

코틀린은 자바에는 없는 수준 높은 타입 추론 시스템을 가지고 있다.

```
val num = 10
val ids = listOf(12, 112, 123, 32)
val name = "HaeChan"
```

이는 개발 시간을 줄여줄 뿐만 아니라 코드의 길이가 짧아지므로 가독성이 증가한다. 하지만 유형이 명확하지 않을 때는 남용하지 않는 것이 좋다.

```
val data = repository.getData()
```

다음과 같은 코드는 타입을 숨기고 있다. 가독성을 위해 코드를 설계할 때는 읽는 사람에게 중요한 정보를 숨겨서는 안 된다.

`함수의 정의를 보며 타입을 확인하면 되지 않나?`
라고 할수도 있지만, 이는 즉 가독성이 떨어지는 것을 의미하며, 깃허브 등의 환경에서는 코드를 읽을 수 없다.
다음과 같이 타입을 지정해주자

```
val data: UserData = repository.getData()
```

[**플랫폼 타입을 사용하지 말라**](https://velog.io/@cksgodl/kotlin-%EC%95%88%EC%A0%95%EC%84%B1%EC%9D%84-%EC%9C%84%ED%95%B4-%EC%B5%9C%EB%8C%80%ED%95%9C-%ED%94%8C%EB%9E%AB%ED%8F%BC-%ED%83%80%EC%9E%85%EC%9D%84-%EC%82%AC%EC%9A%A9%ED%95%98%EC%A7%80-%EB%A7%90%EB%9D%BC)에서 보았듯이 안전을 위해서도 타입을 지정하는 것이 좋다.

### 리시버를 명시적으로 참조하라

함수와 프로퍼티를 지역 또는 톱레밸 변수가 아닌 다른 리시버로부터 가져올 때가 있다.

```
viewModel.responseData.observe(viewLifecycleOwner) { response ->
      response?.let {
      		binding.apply {
			// ...
        	}
      }
}
```

- observe()를 참조하는 리시버 `response`
- let()을 잠조하는 리시버 `it`
- binding()을 참조하는 리시버 `this`

이렇게 여러개의 리시버가 있는 경우 `response`와 같이 내부에 리시버를 명시적으로 나타내면 좋다.

특히 범위지정함수 apply, also, with, run 등과 같이 사용할 때가 대표적인 예이다.

레이블 없이 리시버를 활용하면 가장 가까운 리시버를 의미한다. 외부에 있는 리시버를 사용하려면 레이블을 사용해야 한다.

두 예제를 살펴보자.

```
class Node(val name: String){
	fun makeChild(childName: String) =
    	create("$name.$childName").apply {
			print("Created ${this?.name} in " + " ${this@Node.name}")
		}

	fun create(name: String): Node? = Node(name)
}

fun main() {
	val node = Node("parent")
    node.makeChild("child")
    // Created parent.child in parent
}
```

이렇게 명확하게 작성하면, 코드를 안전하게 사용할 수 있을 뿐더러 가독성도 향상된다.

> 짧게 적을 수 있다는 이유로 리시버를 제거하지 말기
> 여러개의 리시버가 있으면 명시적으로 리시버를 지정하기
