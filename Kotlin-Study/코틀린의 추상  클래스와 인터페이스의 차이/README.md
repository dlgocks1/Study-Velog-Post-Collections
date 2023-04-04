[Kotlin: why use Abstract classes (vs. interfaces)? - StackOverFlow
](https://stackoverflow.com/questions/45616548/kotlin-why-use-abstract-classes-vs-interfaces)

### 추상클래스와 인터페이스??

추상클래스는 상태를 가질 수 있다. (ex var.. 과 같은 변수들)
또한 클래스는 여러 인터페이스를 상속받을 수 있지만 두개 이상의 추상클래스는 상속 받을 수 없다.

그렇다면 왜 인터페이스와 추상클래스 중 어떤것을 써야할까?
인터페이스에서도 추상클래스와 같이 구체적인 기능 구현을 지원하는데 왜 굳이 추상클래스를 써야 하는가?

```
interface Shiny {

    fun shine(amount : Int)  // 추상 클래스

    fun reflect(s : String) { print ("**$s**") }  // 구체적인 기능 구현

}
```

---

추상 클래스의 실용적인 측면은 상태와 상속받은 클래스에서 Override된 상태를 캡슐화하여 파생 클래스에서 재정의할 수 없다는 것이다.

즉 추상 클래스를 상속받은 파생 클래스에서 상태를 재정의할 수 없다는 것이다.

```
abstract class HundaiCar() {
    var company: String = "Hundai"
}

class car : HundaiCar(){
    override var company = "??" // Make HundaiCar.company Open
}
```

해당 상태를 오버라이드 받아도 상태가 Open이지 않으면 이를 건드릴 수 없다. -> 상속받은 파생 클래스를 상태를 재정의할 수 없다.

Override를 허용하는 변수, 함수에는 open 접근자를 붙여 이를 표시한다.

인터페이스를 상속받은 클래스는 해당 속성을 재정의해야 한다. (백킹 필드 또는 사용자 지정 접근자 사용가능)

```
interface HundaiCar {
    var company: String
}

class Car : HundaiCar{
    override var company: String
        get() = "company"
        set(value) { println("Just Ignoring") }
}

fun main() {
    val car = Car()
    println(car.company) // company
    car.company = "KIA"
    println(car.company) // Just Ignoring 출력 및 company 그대로
}

```

인터페이스를 상속받은 클래스는 이러한 백킹 필드를 재 정의할 수 있다.
즉, 상속받은 클래스가 예기치 않은 방식으로 속성을 재정의할 수 있다.

> 인터페이스에서는 신뢰할 수 있는 방식으로 상태를 저장할 수 없다.
> 왜냐하면 상속받은 클래스가 예기치 않은 방식으로 속성을 재정의할 수 있기 때문이다.

```
interface MyContainer {
    var size: Int

    fun add(item: MyItem) {
        // ...
        size = size + 1
    }
}
```

여기에서는 Size 증가시키는 추가를 위한 함수를 제공한다.
그러나 이를 상속받은 클래스가 다음과 같이 정의되면 에러가 발생할 수 있다.

```
class MyContainerImpl : MyContainer {
    override var size: Int
        get() = 0
        set(value) { println("Just ignoring the $value") }
}
```

추상 클래스는 상태 Size에 대한 변화를 허용하지 않으며, 정의된 모든 함수에 대해 상태 Size가 변화하지 않을 것이라 장담할 수 없다.

또 다른 예를 보자

```
interface HundaiCar{
    var logo = "logo"
}

class Car: HundaiCar{
	override var logo: String
        get() = "hyndai"
        set(value) = Unit
}

fun main(){
    val car = Car()
    println(Car().logo) // hyndai
    car.logo = "KIA"
    println(Car().logo) // hyndai
}
```

Car 클래스내에서 backing field의 set을 Unit으로 설정해놨기 떄문에 변경이 불가능하다.

** 즉, 인터페이스를 상속받는 클래스에서는 동일하게 상태가 유지되는 되는 것을 보장 받을 수 없다. **

---

이와는 별도로 추상 클래스는 내부에 final변수를 가질 수 있는 반면, 인터페이스의 구현에서는 private 멤버만 가질 수 있다.

"그 외에도 추상 클래스는 private 및 final 변수를 가질 수 있지만 인터페이스는 그렇지 않다."

![](https://velog.velcdn.com/images/cksgodl/post/c0abaa81-dc81-4c5a-8b70-f645d12ac1ea/image.png)

## 정리

interface에서는 final변수는 생성이 불가능하며, 상태를 정의할 수 있지만 상태에 대한 backing property가 디폴트 프로퍼티라고는 장담하지 못한다.

interface에서 구현한 상태 (var num: Int)에 대해서 작동하는 함수

```
fun addnum(){
	this.num +=1
}
```

이 올바르게 작동할 것이란 장담은 할 수 없다. ( set property가 Unit으로 지정될 수도 있기 때문)

하지만 추상클래스 에서 정의한 상태는 디폴트 프로퍼티, 백킹 프로퍼티까지 모두 추상클래스에서 정의하며,
이를 상속받은 클래스에서 오버라이드를 허용하려면 open키워드를 붙여 사용해야한다.

즉, 오버라이드를 허용하지 않는 상태에 대해 추상클래스에서 상태를 사용하는 기능(함수)도 올바르게 작동할 것이라 장담할 수 있을 것이다.
