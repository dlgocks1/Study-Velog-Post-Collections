### infix란?

[kotlinlang.org - infix](https://kotlinlang.org/docs/functions.html#variable-number-of-arguments-varargs)

Infix 함수는 두개의 변수 가운데 오는 함수를 의미한다.
코틀린에서 기본적으로 정의된 Infix 함수들 중에 Pair를 만드는 to가 있습니다.

```
val pair : Pair<String, String> = "White" to "0xffffff"

0 until 100

0 .. 200
```

infix 함수 선언은 다음의 룰을 따라야 한다.

- 확장함수의 형태로 선언되어야 한다.

- 하나의 파라미터을 꼭 가져야 한다.

- 파라미터로는 가변인자를 사용할 수 없으며 기본값이 없어야 한다.

```
infix fun Int.infixFun(a: Int) : Int {
	// ...
}
infix fun String.addStringToFloat(f : Float) : String {
	// ...
}

// Infix 함수 활용
"Hello" addStringToFloat 4f

// 확장 함수 활용
"Hello".addStringToFloat(4f)
```

- infix 함수 호출은 산술 연산자`(+,-,*,/)`, 유형 캐스트`(as Int)` 및 rangeTo 연산자보다 우선 순위가 낮다.

```
1 shl 2 + 3 is equivalent to 1 shl (2 + 3)

0 until n * 2 is equivalent to 0 until (n * 2)

xs union ys as Set<*> is equivalent to xs union (ys as Set<*>)
```

- `부울연산자(&&,||)`, `is`, `in` 체크 연산자보다 우선순위가 높다.

```
a && b xor c is equivalent to a && (b xor c)

a xor b in c is equivalent to (a xor b) in c
```

- infix 기능은 항상 리시버와 파라미터를 모두 지정해야 한다. infix 표기법을 사용하여 현재 리시버에서 메서드를 호출할 때, 해당 메서드를 명시적으로 사용할 수 있다.

클래스 내에 정의하면 dispatcher가 클래스 자신이기 때문에 생략할 수 있다.

```
class MyStringCollection {
    infix fun add(s: String) { /*...*/ }

    fun build() {
        this add "abc"   // Correct
        add("abc")       // Correct
        //add "abc"        // Incorrect: the receiver must be specified
    }
}
```

---

#### 실제로 사용해보기

서버에서 오는 배열을 객체내의 값에 따라 임의의 순서에 맞게 재 정렬을 하고 싶다.

```
private fun setRataioList(cloverCounts: List<CloverCount>): List<String> = listOf(
      cloverCounts.find {
        it.method == "Turn"
      }?.count ?: 0 ,
      cloverCounts.find {
        it.method == "ManyYears"
      }?.count ?: 0 ,
      cloverCounts.find {
        it.method == "Used"
      }?.count ?: 0 ,
      cloverCounts.find {
        it.method == "Attachment"
      }?.count ?: 0 ,
      cloverCounts.find {
        it.method == "Reform"
      }?.count ?: 0 ,
      cloverCounts.find {
        it.method == "Eco"
      }?.count ?: 0 ,
```

`method`이름이 `Turn`인 객체의 Count가 제일 앞에 오도록 하고 그다음 순서대로 지정하는데 소스가 많이 복잡하고 더럽다.

```
  private infix fun List<CloverCount>.findMethodCount(method: String): Int {
    return this.find {
      it.method == method
    }?.count ?: 0
  }
```

소스의 가독성을 위해 `infix` 함수를 선언하고 내부의 로직을 따로 함수로 추출하자.

```
  private fun setRataioList(cloverCounts: List<CloverCount>): List<Int> = listOf(
    cloverCounts findMethodCount "Turn",
    cloverCounts findMethodCount "ManyYears",
    cloverCounts findMethodCount "Used",
    cloverCounts findMethodCount "Attachment",
    cloverCounts findMethodCount "Reform",
    cloverCounts findMethodCount "Eco",
  )
```

`infix`함수를 사용하여 소스를 다시보았을 때 훨씬 깔끔해 진것을 알 수 있다.

### 코틀린 내에서의 Builder pattern

#### builder pattern을 사용하는 이유가 무엇인가?

1. 클래스를 만드는 아규먼트들이 너무 많아서 햇갈릴 때(생성자 파라미터가 너무 많을 때)
2. 해당 아규먼트의 설정 순서가 상관이 없다.
3. 해당 아규먼트에 대한 default 값 설정이 가능하다.
   라고 생각한다.

이러한 이유에서라면 코틀린에서는 builder pattern을 적용할 필요가 없다.
왜냐하면 kotlin에서는 이 모든것을 이미 지원하고 있기 때문이다.

```
data class Car(
	val model: String? = null,
    val year: Int = 0 // default 값 설정
)

// use it like so
val hundaiCar = Car(model="H",year=5) // 해당 파라미터에 직접 할당 가능
val doyotaCar = Car(year=1, model="D") // 순서상관 X
```

그럼에도 불구하고 자동차(Car) 클래스를 만들기 위해서 다음과 같은 `Builder pattern`을 사용할 수 있다.

1. Builder를 중첩 클래스로 선언한다.
   Builder를 `companion object`로 선언하는것은 의미가 없다. 왜냐하면 `object`가 싱글톤으로 선언되기 때문이다.
2. 생성자를 주 생성자로 위임하는 보조 생성자를 사용한다.
   생성자를 비공개로 만들고 객체를 인스턴스화할 수 있도록 파라미터로 Builder를 받는다.

```
class Car(
        val model: String?,
        val year: Int
) {

    private constructor(builder: Builder) : this(builder.model, builder.year)

    class Builder {
        var model: String? = null
            private set

        var year: Int = 0
            private set

        fun model(model: String) = apply { this.model = model }

        fun year(year: Int) = apply { this.year = year }

        fun build() = Car(this)
    }
}

// Usage
val car = Car.Builder().model("X").build()
```

#### builder DSL

[type-safe builder](https://kotlinlang.org/docs/type-safe-builders.html)
type-safe builders를 사용하면 코틀린에서 타입 세이프, 정적인 타입의 빌더를 만드는 것이 가능하다.
이는 코틀린 코드를 markup 언어(ex HTML, XML)처럼 사용가능하게 해준다.

`type-safe builder`를 사용하면 복잡한 계층적 데이터 구조를 선언적 방식으로 구축하는 데 적합한 Kotlin 기반 도메인 특정 언어 (DSL)를 만들 수 있다.

#### DSL 이란?

DSL은 Domain Specific Language의 약자로 특정 도메인에 국한해 사용하는 언어이다.

```
class Car (
        val model: String?,
        val year: Int
) {

    private constructor(builder: Builder) : this(builder.model, builder.year)

    companion object {
        inline fun build(block: Builder.() -> Unit) = Builder().apply(block).build()
    }

    class Builder {
        var model: String? = null
        var year: Int = 0

        fun build() = Car(this)
    }
}

// Usage
val car = Car.build { model = "X" }
```

apply는 해당 block()을 실행하고 실행된 결과 T를 반환한다.

```
inline fun <T> T.apply(block: T.() -> Unit): T {
    block()
    return this
}
```

참고 자료

https://stackoverflow.com/questions/36140791/how-to-implement-builder-pattern-in-kotlin

https://kotlinlang.org/docs/functions.html#variable-number-of-arguments-varargs

https://toss.tech/article/kotlin-dsl-restdocs

https://codechacha.com/ko/kotlin-infix-functions/
