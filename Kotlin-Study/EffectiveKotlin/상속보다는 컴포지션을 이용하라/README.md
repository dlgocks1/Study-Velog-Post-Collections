예로부터 상속은 굉장히 널리 사용되며 강력한 기능이다.

`is-a`관계의 객체 계층 구조를 만들기 위해 설계되었다. 하지만 관계가 명확하지 않을 때 상속을 사용하려고 한다면, 조금 더 신중해야할 필요가 있다.

> 일반적으로는 상속보다 컴포지션을 사용하는 것이 좋다.

### 간단한 행위 재사용에서의 상속

간단한 코드부터 살펴보자, 프로그래스 바(progress bar)를 어떤 로직처리 전에 출력하고, 처리 후에 숨기는 유사한 동작을 하는 두 클래스가 있다.

```
class ProfileLoader {
	fun load() {
    	// 프로그래스바 보여줌
        // 작업 수행
        // 프로그래스바 숨김
    }
}

class ImageLoader {
	fun load() {
    	// 프로그래스바 보여줌
        // 작업 수행
        // 프로그래스바 숨김
    }
}
```

이러한 경우에 슈퍼클래스를 만들어 공통된 행위를 추출하면은 깔쌈해보인다.

```
abstract class LoaderWithProgress {
	fun load() {
    	// 프로그래스바를 보여 줌
        doTask()
        // 프로그래스바를 숨김
    }

    abstract fun innerLoad()
}

class ProfileLoader: LoaderWithProgress() {

    override fun innerLoad(){
    	// 태스크 작업 수행
    }
}

class ImageLoader: LoaderWithProgress() {

    override fun innerLoad(){
    	// 태스크 작업 수행
    }
}
```

이러한 코드는 간단한 경우에는 문제 없이 동작하지만 몇 가지 문제가 있다.

1. 상속은 하나의 클래스만을 대상으로 할 수 있다. 즉 상속을 사용해서 행위를 추출하다 보면, 다 계층의 거대한 클래스를 생성하게 되고, 깊고 복잡한 계층 구조가 만들어 진다.

2. 상속은 클래스의 모든 것을 가져온다. 따라서 불필요한 함수를 갖는 클래스가 만들어 질 수 있다. -> 이는 인터페이스 분리 원칙을 위반하게 된다.

3. 상속은 이해하기 쉽다. 일반적으로 개발자가 메서드를 읽고, 메서드의 작동 방식을 이해하기 위해 슈퍼클래스를 여러 번 확인해야 한다면 문제가 있는 것이다.

---

이러한 문제점에 대한 대표적인 대안으로는 **컴포지션(Composition)**이 있다.
컴포지션을 사용한다는 것은 객체를 프로퍼티로 갖고, 함수를 호출하는 형태로 재사용하는 것을 의미한다.

```
class Progress {
	fun showProgress() { /* 프로그래스 바를 보여준다. */ }
	fun hideProgress() { /* 프로그래스 바를 숨긴다. */ }
}

class ProfileLoader: LoaderWithProgress() {
	val progress = Progress() // Progress객체를 프로퍼티로 갖는다.

    override fun innerLoad(){
    	progress.showProgress()
    	// 태스크 작업 수행
        progress.hideProgress()
    }
}

class ImageLoader: LoaderWithProgress() {
	val progress = Progress()

    override fun innerLoad(){
    	progress.showProgress()
    	// 태스크 작업 수행
        progress.hideProgress()
    }
}
```

컴포지션을 이용하면 읽는 사람이 코드를 더욱 더 쉽게 이해할 수 있다.
또한 하나의 클래스 내부에서 여러 기능을 재사용할 수 있다.

다음과 같이 프로그래스바, 경고창을 동시에 활용할 때 컴포지션은 빛을 낸다.

```
class ImageLoader: LoaderWithProgress() {
	private val progress = Progress()
	private val finishedAlert = FinishedAlert()

    override fun innerLoad(){
    	progress.showProgress()
    	// 태스크 작업 수행
        progress.hideProgress()
        finishedAlert.show()
    }
}
```

상속은 필요한 것만 가져올 수는 없고, 슈퍼클래스의 모든 것을 가져온다.

하나 이상의 클래스를 상속할 수 없기 때문에, 이러한 작업을 상속을 이용하여 구현하면 복잡한 계층 구조가 만들어 질 것이다.

### 모든 것을 가져올 수밖에 없는 상속

상속은 슈퍼클래스의 메서드, 제약, 행위 등 모든 것을 가져온다.
하지만 상속은 객체의 계층 구조를 나타낼 때 굉장히 좋은 도구이다. 일부분 만을 재사용하기 위한 목적으로는 적합하지 않다. 일부부분 만을 재사용하고 싶다면 컴포지션을 사용하자.

다음과 같은 강아지 클래스를보자.

```
abstract class Dog {
	open fun bark() { }
    open fun sniff() { }
}
```

만약 로봇 강아지를 만들고 싶은데, 로봇 강아지는 bark(짖기)만 가능하고, sniff(냄새 맡기)는 못하게 하려면 어떻게 해야 할까요??

```
ckass RobotDog : Dog() {
	override fun sniff() {
    	throw Error("Operation not supported")
        // 인터페이스 분리 원칙에 위배됨
    }
}
```

이러한 코드는 RobotDog가 필요도 없는 메서드를 갖기 때문에, 인터페이스 분리 원칙에 위배된다.

대부분의 상황에서는 컴포지션을 사용하면 된다. 컴포지션을 사용하면, 이런 설계 문제가 전혀 발생하지 않습니다. 하지만 계층 구조를 표현해야 한다면, 인터페이스를 활용해 다중 상속을 하는 것이 좋을 수도 있다.

[인터페이스와 추상클래스의 차이](https://velog.io/@cksgodl/Kotlin-Abstract-class와-interface의-차이-무엇을-써야-할까)

### 인터페이스 위임

상속을 허용하지 않은 클래스에 새로운 동작을 추가해야 위임을 이용한다.

```
class CounterSet<T>(
    private val innerSet: MutableSet<T> = mutableSetOf()
) : MutableSet<T> by innerSet {
    var elementsAdded: Int = 0
        private set

    override fun add(element: T): Boolean {
        elementsAdded += 1
        return innerSet.add(element)
    }

    override fun addAll(elements: Collection<T>): Boolean {
        elementsAdded += elements.size
        return innerSet.addAll(elements)
    }
}
```

`by`를 통해 포워딩 메서드들을 자동으로 생성할 수 있다.

### 오버라이딩 제한하기

상속은 허용하지만, 메서드는 오버라이드하지 못하게 만들고 싶은 경우가 있다.
이럴때는 open 키워드를 사용한다. open클래스는 open 메서드만 오버라이드할 수 있다.

```
open class Parent{
    fun a() {}
    open fun b() {}
}

class Child: Parent(){
    override fun a() {} // 'a' in 'Parent' is final and cannot be overridden
    override fun b() {}
}
```

### 정리

- 컴포지션은 다른 클래스의 내부적인 구현에 의존하지 않고, 외부에서 관찰되는 동작에만 의존함으로 안전하다.

- 컴포지션은 더 유연하다. 상속은 한 클래스만을 대상으로 할 수 있지만, 컴포지션은 여러 클래스를 대상으로 할 수 있다.

- 컴포지션은 더 명시적이다. 상속을 사용할 때 (this)와 같은 리시버를 따로 명시하지 않아도 된다. 컴포지션을 활용하면, 리시버를 명시적으로 활용해야만한다.

- 컴포지션은 생각보다 번거롭다. 객체를 명시적으로 사용해야 하므로, 대상 클래스에 일부 기능을 추가할 때 이를 포함하는 객체의 코드 모두를 변경해야 한다.

일반적으로 OOP에서는 컴포지션을 활용하는 것이 좋다.

상속은 `is-a`관계일 때 슈퍼클래스를 상속하는 모든 서브클래스는 슈퍼클래스로도 동작할 수 있어야 한다. 슈퍼클래스에서 통과하는 테스트는 서브클래스도 통과할 수 있어야 한다.

예를 들면 뷰위에 사용되는 뷰 요소들이 있다.
![](https://mblogthumb-phinf.pstatic.net/20111120_212/netrance_1321760695636nqSfa_PNG/%B7%B9%C0%CC%BE%C6%BF%F4_%BA%E4%B5%E9%C0%C7_%B0%E8%C3%FE_%B1%B8%C1%B6.png?type=w2)
