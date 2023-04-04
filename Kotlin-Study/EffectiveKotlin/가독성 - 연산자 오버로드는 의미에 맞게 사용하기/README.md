### 연산자 오버로드를 할 때는 의미에 맞게 사용하라

연산자 오버로딩은 굉장히 강력한 기능이지만, 큰 힘에는 큰 책임이 따른다라는 말처럼 위험할 수 있다.

팩토리얼을 구하는 함수를 보자.

```
fun Int.factorial(): Int = (1..this).product()

fun Iterable<Int>.product(): Int =
	fold(1) { acc, i -> acc * i }
```

이 함수는 Int 확장 함수로 정의되어 있음으로 굉장히 편리하게 사용할 수 있다.

팩토리얼은 ! 기호를 사용해 표기한다는 것을 배웠을 것이다. 그럼 이를 활용하여 팩토리얼을 오버로딩할 수 있지 않을까?

```
operator fun Int.not() = factorial() // 연산자 오버로딩
print(10 * !6) // 7200
```

이렇게 사용해도 될까? **물론 안된다.** 이함수의 이름이 `not()`임을 주목하자. 논리 연산에 사용되는 not()을 사용하면 앞으로의 연산에 큰 오해의 소지가 있을 것이다. 이를 함수로 출력하면 다음과 같다.

```
print(10 * 6.not()) // 7200
```

코틀린의 모든 연산자는 다음 표와 같은 구체적인 이름을 가진 함수의 별칭일 뿐이다.

![](https://velog.velcdn.com/images/cksgodl/post/44d4cc69-0dd1-469d-b9b9-ce07b006246f/image.png)

[operator-overloading, kotlinlang.org](https://kotlinlang.org/docs/operator-overloading.html#arithmetic-operators)에 가면 모든 연산자의 함수명을 볼 수 있다.

위의 팩토리얼 처럼 관례에 어긋나게 함수를 오버로딩하여 사용하지 말자.

#### 분명하지 않는 경우

관례를 충족하는지 아닌지 확실하지 않을 때가 있다.

함수를 세 배 한다는 연산자`(*)`는 무슨 의미를 가질까?

어떤 사람은 다음과 같이 이 함수를 세 번 반복하는 새로운 함수를 만들어 낸다고 생각할 수 있다.

```
operator fun Int.times(operation: () -> Unit): ()-> Unit =
	{ repeat(this) { operation() } }

val tripledHello = 3 * { print("Hello") } // 3번 반복 새로운 함수 생성

tripleHello() // 출력 : HelloHelloHello
```

또 다른 어떤 사람은 함수를 3번 호출한다고 이해할 수도 있다.

```
operator fun Int.times(operation: () -> Unit) =	{
	repeat(this) { operation() }
}

3 * tripleHello()
```

이렇게 의미가 명확하지 않다면, infix를 활용한 확장 함수를 사용하는 것이 좋다.
일반적인 이항 연산자처럼 사용할 수 있다.

```
infix fun Int.timesRepeated(operation: ()->Unit) = {
	repeat(ths) { operation() }
}

val tripleHello = 3 timesRepeated { print("Hello") }
tripleHello() // HelloHelloHello
```

infix 함수를 활용하면 내가 원한 연산이 무엇인지를 정확히 적어줄 수 있어 혼돈을 줄일 수 있다.

#### 정리

연산자 오버로딩은 그 이름의 의미에 맞게 사용하자. 연산자 의미가 불확실하다면, 연산자 오버로딩은 사용하지 않는 것이 좋다. infix 확장 함수 또는 톱레벨 함수를 활용하자.
