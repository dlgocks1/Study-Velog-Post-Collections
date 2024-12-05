# 연산 또는 액션을 전달할 때는 인터페이스 대신 함수 타입을 사용하라

대부분의 프로그래밍 언어에는 함수 타입이라는 개념이 없다.
```
// Kotlin에서의 함수 타입
val funcType : () -> Unit = { }
val funcType2 : (Int) -> String = { } 
```
## SAM이란?

그래서 연산 또는 액션을 전달할 때 메서드가 하나만 있는 인터페이스를 활용한다. 이를 SAM(Single-Abstact Method)라고 불른다.

다음은 뷰를 클릭했을 때 발생하는 정보를 전달하는 SAM이다.
```
interface OnClick {
	fun clicked(view: View)
}
```
함수가 SAM을 받는다면 이러한 인터페이스를 구현한 객체를 전달받는다는 의미이다.

```
fun setOnClickListener(listener: OnClick){
	// ..
}

setOnClickListener(object :OnClick{
	override fun clicked(view: View) {
    	// ...
    }
})
```

이런 코드를 함수 타입을 사용하는 코드로 변경하면 더 많은 자유를 얻을 수 있다.

```
fun setOnClickListener(listener: (View) -> Unit) {
	// ...
}

// 다음과 같이 사용
setOnClickListener { /*...*/ }
setOnClickListener(fun(view) { /*..*/ })
setOnClickListener(::println)
setOnClickListener(this::showUsers)
```

SAM의 장점으로는 아규먼트에 이름을 붙일 수 있지만, 이는 kotlin의 `type aliase`를 사용하면 함수 타입도 이름을 붙일 수 있다.
```
typealias OnClick = (View) -> Unit
```

### SAM은 언제 사용해야할까
코틀린이 아닌 다른 언어에서 사용할 클래스를 설계할 때에는 함수타입보다 SAM을 사용하는 것이 합리적이다.

```
// 코틀린
class CalanderView() {
	var onDateClicked: ((date: Date) -> Unit)? = null 
    // 타 언어세어 코틀린의 함수타입을 사용하려면 Unit을 명시적으로 리턴하는 함수가 필요하다.
    var onPageChanged: OnDateClicked? = null
}

interface OnDateClicked {
	fun onClick(date: Date)
}

// 자바
CalendarView c = new CalendarView();
c.setOnDateClicked(date -> Unit.INSTANCE);
c.setOnPageChanged(date -> {});
```

# 상태 패턴

### 상태 패턴이 무엇인가

[상태 패턴을 사용해보자 - 테코블](https://tecoble.techcourse.co.kr/post/2021-04-26-state-pattern/)


`상태 패턴`은 객체의 내부 상태가 변화할 때, 객체의 동작이 변하는 소프트웨어 디자인이다. 상태 패턴은 컨트롤러, 프레젠터, 뷰 모델을 설계할 때 많이 사용된다.(MVC, MVP, MVVM 아키텍쳐 등)

동일한 메서드가 상태에 따라 다르게 동작할 때 사용할 수 있는 패턴이 상태 패턴(State Pattern)이다. 

> 상태 패턴은 특정 기능을 수행한 후 다음 상태를 반환한다.

>상태 패턴을 사용한다면 서로 다른 상태를 나타내는 클래스를 만들게 된다. 그리고 현재 상태를 나타내기 위한 읽고 쓸 수 있는 프로퍼티도 만들게 된다.

```
상태변경(행위) {
	return 다음상태
}
```

다음과 같은 예를 보자.

`운동하기` 🎾, `밥먹기` 🥘, `자기` 😴와 같은 행동을 취할 수 있을 때 나의 기분을 상태패턴으로 표현하면 다음과 같다.
```
interface Behavior {
    fun exercize() : Behavior
    fun getMeal() : Behavior
    fun sleep() : Behavior
    fun printCurrentEmotion() {
        println(this.javaClass.name)
    }
}
```

상태 패턴은 특정 기능을 수행한 후 다음 상태를 반환한다.

```
sealed class MyEmotion : Behavior{
    object Happy : MyEmotion() {
        override fun exercize(): Behavior = Tired

        override fun getMeal(): Behavior = Satisfied

        override fun sleep(): Behavior = Satisfied

    }

    object Tired : MyEmotion() {
        override fun exercize(): Behavior = Satisfied

        override fun getMeal(): Behavior = Happy

        override fun sleep(): Behavior = Happy

    }

    object Satisfied : MyEmotion() {
        override fun exercize(): Behavior = Tired

        override fun getMeal(): Behavior = Satisfied

        override fun sleep(): Behavior = Happy
    }

}
```

---

```
val myEmotion = MyEmotion.Happy
myEmotion.exercize().apply {
        printCurrentEmotion()
    }.getMeal().apply {
        printCurrentEmotion()
    }
```

![](https://velog.velcdn.com/images/cksgodl/post/12af9b4d-1f28-428a-b7d4-3f913f9a12c8/image.png)

같은 객체 myEmotion에 대해 printCurrentEmotion을 실행해도 다른 결과가 반환된다. 이와 같이** 동일한 메서드가 상태에 따라 다르게 동작할 때 사용할 수 있는 패턴이 상태 패턴(State Pattern)이다.**

> 상태패턴이란 객체 지향 방식으로 상태 기계(한 번에 오로지 하나의 상태만을 가지게 되며, 현재 상태(Current State)란 임의의 주어진 시간의 상태를 칭함)를 구현하는 행위 소프트웨어 디자인 패턴이다. 


상태패턴에서 클래스를 추가하더라도 기존의 메서드의 코드는 그대로 유지된다. 또한 상태에 따른 동작을 구현한 코드가 상태별로 구분되기 때문에 상태별 동작을 수정하기 쉽다.

새로운 `졸림`상태를 추가하여도 구현된 코드가 기존의 컨텍스트를 침해하는 일이 없다.
```
object Sleepy : MyEmotion() {
    override fun exercize(): Behavior = Tired

    override fun getMeal(): Behavior = Tired

    override fun sleep(): Behavior = Happy
}

```

위에서는 `sealed class`를 사용하여 상태패턴을 구현하였지만 Enum class를 활용하여서도 이를 구현할 수 있다.

### Enum(열거형)이란
서로 연관된 상수들의 집합이며 이는 상태를 나타내기 편리한 방식이다.

다음은 열거형 클래스를 사용해 기분을 표현한 것이다.
```
enum class MyEmotion {
    Happy,
    Tired,
    Satisfied,
    Sleepy;

    fun exercize(): MyEmotion{
        return when(this){
            Happy -> Satisfied
            Tired -> {
                println("Im so tired..!")
                Tired
            }
            Satisfied -> Tired
            Sleepy -> Sleepy
        }
    }

    fun getMeal() : MyEmotion {
        return when(this){
            Happy -> Satisfied
            Tired -> Happy
            Satisfied -> Happy
            Sleepy -> Sleepy
        }
    }

    fun sleep() : MyEmotion {
        return when(this){
            Happy -> Happy
            Tired -> Satisfied
            Satisfied -> {
                println("에너지가 철철")
                Satisfied
            }
            Sleepy -> Satisfied
        }
    }

}
```
```
val myEmotion = MyEmotion.Tired
myEmotion.sleep().sleep().exercize().exercize()
```

![](https://velog.velcdn.com/images/cksgodl/post/8f2a9a1d-4aef-4d6f-bf33-14f0418dfc2b/image.png)

이와같이 enum 에서 조건문을 이용한 방식은 코드를 복잡하게 만들어 유지 보수를 어렵게 한다.

또한 새로운 상태가 추가된다고 하면 모든 동작 함수를 수정해야한다.(when 브런치) 더 더욱 상태가 많아지고 동작이 복잡해지면 코드는 점점 늘어날 것이다.
이렇게 if, when 브런치를 사용해 Enum값을 판단하는 것은 OCP(개방폐쇄원칙)을 준수하지 못한다. 

### Compose에서의 상태패턴 및 `Sealed Class` 사용 👍

[네트워크 결과값을 Flow변환 및 Sealed 클래스로 관리하기](https://velog.io/@cksgodl/AndroidKotlin-%EB%84%A4%ED%8A%B8%EC%9B%8C%ED%81%AC-%EA%B2%B0%EA%B3%BC%EA%B0%92%EC%9D%84-Flow%EB%B3%80%ED%99%98-%EB%B0%8F-Sealed-%ED%81%B4%EB%9E%98%EC%8A%A4%EB%A1%9C-%EA%B4%80%EB%A6%AC%ED%95%98%EA%B8%B0)
sealed class는 전에도 네트워크 요청을 처리할 때 사용된 적 있
다.

이와 같이 네트워크 `상태`와 같이 어떤 상태가 정해져 있을 때는 
sealed class를 사용하여 네트워크 요청을 묶어줄 수 있다.

```
@Composable
fun handleUI(){
    val apiResult:ApiResult<ApiResponse> = viewModel.getResult()
    when(apiResult){
        is ApiResult.Empty -> {
            // 로딩바 등등 ... 
        }
        is ApiResult.Success -> {
            // 결과 출력 화면 ...
        }
        is ApiResult.Error -> {
            // 에러 났을 때 화면...
        }
    }
}

sealed class ApiResult<out T> {
    data class Success<out T>(val value: T) : ApiResult<T>()
    object Empty : ApiResult<Nothing>()
    data class Error(
        val exception: Throwable? = null,
        var message: String? = ""
    ) : ApiResult<Nothing>()
}
```

