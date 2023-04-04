TDD기반(테스트를 기반으로 개발을 주도하는 프로젝트)에서 **given-when-then 패턴**은 빼놓을 수 없다.

> given-when-then 패턴이란 1개의 단위 테스트를 3가지 단계로 나누어 처리하는 패턴이다.

- given : 주어진 상황에 대하여
- when : 어떠한 함수를 실행하면
- then : 예상된 결과가 나와야 한다.

---

[유닛테스트 체험하기](https://velog.io/@cksgodl/kotlin-%EC%95%88%EC%A0%95%EC%84%B1%EC%9D%84-%EC%9C%84%ED%95%B4-use%EB%A5%BC-%EC%82%AC%EC%9A%A9%ED%95%98%EC%97%AC-%EB%A6%AC%EC%86%8C%EC%8A%A4%EB%A5%BC-%EB%8B%AB%EC%95%84%EB%9D%BC-%EC%95%88%EB%93%9C%EB%A1%9C%EC%9D%B4%EB%93%9C%EC%97%90%EC%84%9C-%EB%8B%A8%EC%9C%84-%ED%85%8C%EC%8A%A4%ED%8A%B8-%EA%B2%BD%ED%97%98%ED%95%B4%EB%B3%B4%EA%B8%B0)에서 단위테스트를 경험하며 이런 패턴에 맞는 테스트 네이밍을 공부 했었다.

## 단위테스트에서의 네이밍 컨벤션

Unit Test Naming Convention

```
메소드이름_테스트중인상태_예상되는결과
example: isAdult_AgeLessThan18_False

메소드이름_예상결과_테스트중인상태
example: isAdult_False_AgeLessThan18

test테스트를 수행하는 상태(특징)
example: testIsNotAnAdultIfAgeLessThan18

테스트를 수행하는 상태(특징) = FeatureToBeTested
example: IsNotAnAdultIfAgeLessThan18

Should_예상 결과값_When_테스트 중인 상태
example: Should_ThrowException_When_AgeLessThan18

When_테스트 중인 상태_예상 결과
example: When_AgeLessThan18_Expect_isAdultAsFalse

Given_초기 상태_When_테스트하는 상황_Then_예상결과
example: Given_UserIsAuthenticated_When_InvalidAccountNumberIsUsedToWithdrawMoney_Then_TransactionsWillFail
```

해당 네이밍에 맞추어 간단한 예를 작성해보자.

```
@Test
@DisplayName("Given_Math.max함수에대해_When_2와 5가 주어졌을 때_Then_5가 반환되어야한다.")
fun kotlinMathMaxTest() {
	assertThat(max(2,5)).isEqualTo(5)
}
```

![](https://velog.velcdn.com/images/cksgodl/post/c5f7b770-d30b-45ed-a3e8-9951d6103ac9/image.png)

## `DSL`을 만들어 상황을 출력해보자.

이러한 상황, 조건, 결과에 대한 내용을 제목에 몰아넣기 보다 직접 출력해보자.

지금부터 만들어볼 것은 코틀린 진영에서 가장 많이 사용되는 테스트 프레임워크인 `Kotest`을 따라해보는 것이다. 이는 코틀린 DSL을 활용해 테스트 코드를 작성할 수 있으며 더 많은 기능은 다음 링크를 참고하자

[우아한 형제들 기술블로그 - 코틀린 DSL과 테스트](https://techblog.woowahan.com/5825/)

다음은 `Kotest`의 `BehaviorSpec`의 예이다.

```
internal class CalculatorBehaviorSpec : BehaviorSpec({
    val sut = Calculator()

    given("calculate") {
        val expression = "1 + 2"
        `when`("1과 2를 더하면") {
            val result = sut.calculate(expression)
            then("3이 반환된다") {
                result shouldBe 3
            }
        }

        `when`("수식을 입력하면") {
            then("해당하는 결과값이 반환된다") {
                calculations.forAll { (expression, answer) ->
                    val result = sut.calculate(expression)

                    result shouldBe answer
                }
            }
        }

        `when`("입력값이 null이거나 빈 값인 경우") {
            then("IllegalArgumentException 예외를 던진다") {
                blanks.forAll {
                    shouldThrow<IllegalArgumentException> {
                        sut.calculate(it)
                    }
                }
            }
        }

        `when`("사칙연산 기호 이외에 다른 연산자가 들어오는 경우") {
            then("IllegalArgumentException 예외를 던진다") {
                invalidInputs.forAll {
                    shouldThrow<IllegalArgumentException> {
                        sut.calculate(it)
                    }
                }
            }
        }
    }
}) {
    companion object {
        private val calculations = listOf(
            "1 + 3 * 5" to 20.0,
            "2 - 8 / 3 - 3" to -5.0,
            "1 + 2 + 3 + 4 + 5" to 15.0
        )
        private val blanks = listOf("", " ", "      ")
        private val invalidInputs = listOf("1 & 2", "1 + 5 % 1")
    }
}
```

![](https://velog.velcdn.com/images/cksgodl/post/a0039520-3661-40e5-9e3c-137ebbd138d4/image.png)

`Given`, `When`, `Then`의 상황을 나누어 결과로 보여준다. 이는 가독성이 좋으며 정해진 테스트의 패턴도 맞출 수 있다. 이를 직접 `DSL`을 활용해 구현해보자.

---

첫 번째로 `infix`를 활용하여 코드가 실제로 말하듯이 테스트 코드를 작성해보자.

```
@Test
@DisplayName("문자열이 해당 단어로 시작하는지 테스트한다.")
fun stringStartWithATest() {
    "ABCD" lessThan 5 startWith "A"

    "ABCD".lessThan(5).startWith("A") // 동일
}
```

위의 테스트는 String이 5이하인지, `A`로 시작하는지 테스트한다. 이는 `infix`를 활용해 유용한 테스트 함수를 만들 수 있음을 의미한다.

```
infix fun String.startWith(startStr: String): String {
    assertThat(this).startsWith(startStr)
    return this
}

infix fun String.lessThan(size: Int): String {
    assertThat(this.length).isLessThan(size)
    return this
}
```

빈 `object`를 사용하여 꼼수를 활용하면 `infix`사이에 문자열을 하나 더 넣을 수 있다. `equal`과 `to`는 이미 사용중인 예약어라 `으로 감싸서 처리했다.

이런 예는 `DSL`을 구성하는 방법 중 상대적으로 복잡한 방법이다. 하지만 이런 결과는 아주 멋지므로 한번쯤 만들어볼만 하다. `infix`호출과 `object`로 정의한 싱글턴 객체 인스턴스를 조합하면 `DSL`에 상당히 복잡한 문법을 도입할 수 있고, 구문을 깔끔하게 만들 수 있다.

```
@Test
fun mathMaxTest() {
	val num1 = 2
    val num2 = 5
	max(num1, num2) should `equal` `to` 5
}

object `equal`

infix fun <T> T.should(x: Any): InfixWrapper<T> = InfixWrapper(this)

class InfixWrapper<T>(val value: T) {
  	infix fun `to`(prefix: T) {
  		assertThat(value).isEqualTo(prefix)
	}
}

```

해당 싱글톤 객체와 함께 `Then`, `When`, `Given`함수를 만들어 `kotest`라이브러리와 비슷하게 테스트를 진행할 수 있다.

```
fun Then(state: String, action: () -> Unit) {
    println(state)
    action()
}

fun When(state: String, action: () -> Unit) {
    println(state)
    action()
}

fun Given(state: String, action: () -> Unit) {
    println(state)
    action()
}


@Test
fun givenWhenThenTest() {
    Given("Kotlin의 Math.max()") { // 어떤 생성자가 생성될 때
        When("2와 5라는 숫자가 입력됬을 때") {
            val num1 = 2
            val num2 = 5
            Then("5를 반환한다.") {
                assertThat(max(num1, num2)).isEqualTo(5)
                max(num1, num2) should `equal` `to` 5
            }
        }
    }
}

Given : JVM의 Math.max()
When : 2와 5가 주어졌을 때
Then : 5가 반환된다.
```

---

커스텀 테스트 함수를 따로 구현하여 다음과 같이 구현할 수도 있다.

```
private fun customTest(Given: String, When: String, Then: String, action: () -> Unit) {
    println("Given : $Given")
    println("When : $When")
    println("Then : $Then")
    action()
}

@ParameterizedTest
@CsvSource("2,5,5", "1,3,3", "20,50,50") // , delimiter = ',')
fun formattedTest(num1: Int, num2: Int, maxNum: Int) = customTest(
    Given = "JVM의 Math.max()",
    When = "${num1}와 ${num2}가 주어졌을 때",
    Then = "${maxNum}가 반환된다."
) {
    max(num1, num2) should `equal` `to` maxNum
}
```

![](https://velog.velcdn.com/images/cksgodl/post/7d26a7a9-e861-4a10-a0f9-9085fc9a6485/image.png)

`println`으로 주어진 패턴에 따른 결과 값을 출력하고, 테스트 패턴에 따른 상황을 입력하지 않으면 에러가 난다.

`DSL`의 활용은 무궁무진하다. 안드로이드의 `Anko`라이브러리도 `DSL`을 활용하고 있고 [버튼을 생성하는 DSL을 만들어 Compose같이 버튼을 만들어보자](https://velog.io/@cksgodl/AndroidKotlin-%EB%B2%84%ED%8A%BC%EC%9D%84-%EC%83%9D%EC%84%B1%ED%95%98%EB%8A%94-DSL%EC%9D%84-%EB%A7%8C%EB%93%A4%EC%96%B4-Compose%EA%B0%99%EC%9D%B4-%EB%B2%84%ED%8A%BC%EC%9D%84-%EB%A7%8C%EB%93%A4%EC%96%B4%EB%B3%B4%EC%9E%90)에서도 `DSL`을 활용해 버튼을 만드는 방법을 제공하고 있다.
