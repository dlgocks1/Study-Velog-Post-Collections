여러 잘 정리된 소스를 보면 다음과 같이 with, apply와 같은 함수를 활용하여 소스를 간결화 한것을 볼 수 있다.

```
with(UserApiClient.instance) {
	// ...
}
binding.apply{
	// ...
}
with(viewModel) {
	// ...
}
```

얘네들은 뭐하는 놈들이고 어떻게 사용해야 잘 사용하는 것일까?

## Scope Function(범위 지정 함수)

범위지정함수란 무엇일까?
특정 객체에 대한 작업을 하나의 코드 블록내에서 실행하는 것을 목적으로 하는 함수이다.

특정 객체에 대한 작업을 블록안에 넣으면 가독성 증가 및 유지보수가 쉬워진다.

Kotlin에서는 다음과 같은 범위 지정함수를 지원한다.

- run
- apply
- let
- with
- also

### 수신객체 지정 람다(함수)

범위 지정함수는 기본적으로 매우 비슷한 기능을 하며 2가지 구성요소를 가진다.

1. 수신 객체
2. 수신 객체 지정 람다 ([lambda with receiver](https://kotlinlang.org/docs/lambdas.html#function-literals-with-receiver))

#### 수신객체

> 확장 함수가 호출되는 대상이 되는 값(객체)를 의미한다.

무엇을 수신 받는다 -> 확장함수의 코드를 실행할 대상이 된다.

![](https://velog.velcdn.com/images/cksgodl/post/0a4dfd8c-da7a-450d-9610-38fb46226eba/image.png)

`binding.apply`에서는 `this`가 수신객체로 활용되었고, 수신객체의 타입은 `FragmentLoginBinding`이다.

클릭리스너에서는 `it`이 수신객체로 활용되고 있으며, `View!`가 수신객체의 타입이다.

#### 수신객체 지정 람다(함수)

범위 지정함수는 수신 객체 지정 람다(함수)라고 불리기도 한다.

> 블록 람다식에서 수신객체를 **람다의 입력 파라미터** 또는 **수신객체**로 사용하기 때문에 수신객체를 명시하지 않거나, it을 호출하는 것만으로 람다 안에서 수신객체의 메서드를 호출할 수 있게 해준다.

```
inline fun <T, R> with(receiver: T, block: T.() -> R): R {
    return receiver.block()
}
```

`with`에서는 수신객체로 `receiver: T`를 사용하고 있으며, 수신객체 지정 람다로 `block`을 사용하고 있다.

수신객체지정 람다는 말그대로 수신객체를 지정하는 람다식을 의미한다.

---

```
inline fun <T> T.apply(block: T.() -> Unit): T {
    block()
    return this
}

inline fun <T, R> T.run(block: T.() -> R): R {
    return block()
}

inline fun <T, R> with(receiver: T, block: T.() -> R): R {
    return receiver.block()
}

inline fun <T> T.also(block: (T) -> Unit): T {
    block(this)
    return this
}

inline fun <T, R> T.let(block: (T) -> R): R {
    return block(this)
}
```

#### 왜 이런 범위지정함수를 5개씩이나 만들어 놨을까?

```
inline fun <T, R> with(receiver: T, block: T.() -> R): R {
    return receiver.block()
}
inline fun <T> T.also(block: (T) -> Unit): T {
    block(this)
    return this
}
```

`with`와 `also`의 차이점은 무엇일까?

1. 범위 지정함수를 호출할 때 수신객체의 전달방식이 다르다.
   `with`는 수신객체를 람다의 매개 변수T로 제공한다. -> 이를 명시적으로 제공되는 수신객체라고 한다.
   `also`는 수신객체를 함수의 파라미터로 제공한다.

2. 범위 지정 함수에 전달된 수신객체가 다시 수신 객체 람다에 어떠한 형식으로 전달될 것인가?
   `with`는 수신객체지정 함수가 T의 확장함수형태로 코드블럭 내에 수신 객체가 암시적으로 전달된다.
   `also`는 수신객체지정 함수에 매개변수 T가 코드블록내에 파라미터로 명시적으로 전달된다.

3. 범위지정 함수의 최종적인 반환 값은 무엇인가?
   `with`는 람다를 실행한 결과를 반환한다.
   `also`는 코드 블록 내에 전달된 수신객체를 그대로 다시 반환합니다.

![](https://velog.velcdn.com/images/cksgodl/post/f7625ae7-e58f-4490-b09b-609184ec74bf/image.png)

---

kotlin에서 람다(함수)파라미터를 넘겨주는 방법은 다음과 같다.

```
// 기본형
view.onClick({ toast(it.toString())} ) // 1
view.onClick() { toast(it.toString()) } // 2
view.onClick { toast(it.toString()) } // 3
```

3번은 함수가 명시적으로 하나의 파라미터만 가질 경우

---

### 각각의 범위 지정 함수 사용규칙

#### Apply

```
public inline fun <T> T.apply(block: T.() -> Unit): T {
    block()
    return this
}
```

수신객체의 내부 프로퍼티를 수정하고 수신객체 자체를 반환하기 위해 사용되는 함수
객체 생성 시에 다양한 프로퍼티를 설정해야 하는 경우 사용된다.

```
val pizza = Food().apply {
    name = "domino"
    kcal = 450
}
binding.apply{
	view1.visiblility = //...
    view2.setOnClickListener{ //... }
    view3...
}
```

### run

```
public inline fun <T, R> T.run(block: T.() -> R): R {
    return block()
}
```

apply와 동일하게 동작하지만, 수신 객체를 return하지 않고, run 블록의 마지막 라인을 return한다.
수신객체에 대한 특정한 동작을 수행 한후 리턴 값이 필요할 경우 사용한다.

```
data calss Person(
	var temperature: Float = 36.5f
) {
	fun isSick(): Boolean = temperature > 37.5f
}

fun main(){
	val person = Person().apply{
    	temperature = 37f
    }
    val isPersonSick = person.run{
    	temperature = 37.7f
        isSick()
    }
    println(isPersonSick) // true
}
```

#### with

```
public inline fun <T, R> with(receiver: T, block: T.() -> R): R {
    return receiver.block()
}
```

Non-nullable 수신 객체이고, 블럭의 반환값이 필요하지 않을 때 사용한다.

```
val person: Person = getPerson()
with(person) {
    print(name)
    print(age)
}
```

#### let

```
public inline fun <T, R> T.let(block: (T) -> R): R {
    return block(this)
}
```

수신객체를 이용한 확장함수이며, 확장함수를 실행한 후 반환값을 리턴한다.

```
val name = person?.let {it.name} ?: "NoName"
```

1. 지정된 값이 null이 아닌 경우 코드를 실행해야 하는경우
2. Nullable 객체를 다른 Nullable 객체로 변환하는 경우
3. 단일 지역 변수의 범위를 제한하는 경우

`?.let` null safe(?)와 같이사용하여서 null체크를 할 수 있다. -> `block`은 수신객체가 null이 아닐때만 수행됨으로

#### also

```
public inline fun <T> T.also(block: (T) -> Unit): T {
    block(this)
    return this
}
```

also는 apply와 마찬가지로 수신객체 자신을 반환한다.

그러나 수신 객체를 전혀 사용하지 않거나, 수신 객체의 속성을 변경하지 않고 사용하는 경우 사용한다.

객체의 사이드이펙트를 확인하거나, 해당 데이터의 유효성을 검사할 때 사용한다.

### 범위 지정 함수의 중첩

범위 지정 함수가 중첩되면 코드의 가독성이 떨어지고 파악하기 어려워진다.

또한 수신 객체가 중첩되며 이를 혼동하기 쉽다.
`apply`,`run`,`with`는 수신객체가 암시적으로 전달되어 this 또는 생략하여 사용되고, 수신객체의 이름을 다르게 지정할 수 없기 때문에 중첩될 경우 혼동하기 쉽다.

`also`와 `let`을 중첩 해야만 할 때는 암시적 수신 객체를 가르키는 it을 사용하지 말아야한다. 명시적인 이름을 따로 만들어 코드에서 이름이 혼동되지 않게 한다.

---

참고 자료

https://medium.com/@limgyumin/%EC%BD%94%ED%8B%80%EB%A6%B0-%EC%9D%98-apply-with-let-also-run-%EC%9D%80-%EC%96%B8%EC%A0%9C-%EC%82%AC%EC%9A%A9%ED%95%98%EB%8A%94%EA%B0%80-4a517292df29

https://blog.yena.io/studynote/2020/04/15/Kotlin-Scope-Functions.html

https://kotlinworld.com/255

https://velog.io/@rhkswls98/Android-Kotlin-apply-with-let-also-run-%EC%A0%95%EB%A6%AC

https://medium.com/@limgyumin/%EC%BD%94%ED%8B%80%EB%A6%B0-%EC%9D%98-apply-with-let-also-run-%EC%9D%80-%EC%96%B8%EC%A0%9C-%EC%82%AC%EC%9A%A9%ED%95%98%EB%8A%94%EA%B0%80-4a517292df29
