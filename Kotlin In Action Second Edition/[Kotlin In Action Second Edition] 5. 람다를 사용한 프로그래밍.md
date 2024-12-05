람다 표현식 또는 간단히 람다라고도 하는 람다는 본질적으로 다른 함수에 전달할 수 있는 작은 코드 덩어리를 의미한다.

이후에서 아래의 내용을 다룬다.

- 람다식 및 멤버 참조를 사용하여 함수에 코드 및 동작 스니펫 전달하기
- `Kotlin`에서 함수형 인터페이스 정의하기 및 Java 함수형 인터페이스 사용하기
- 수신기와 함께 람다 사용


## 5.1 람다 표현식 및 멤버참조

`Java 8`에 람다를 도입한 것은 언어의 진화 과정에서 가장 오랫동안 기다려온 변화 중 하나였다. 왜 그렇게 큰 이슈였을까? 

### 5.1.1 람다에 대해 소개!: 값으로서의 코드 블록

코드에서 동작을 전달하고 저장하는 작업은 자주 하는 일이다. 예를 들어, "이벤트 가 발생하면 이 핸들러 실행" 또는 "데이터 구조의 모든 요소에 이 연산 적용"과 같은 아이디어를 표현해야 할 때가 많다. 이전 버전의 Java에서는 익명 내부 클래스를 통해 이러한 작업을 수행할 수 있었다. 

이 문제를 해결하기 위한 또 다른 접근 방식이 있는데, __바로 함수를 값으로 취급하는 기능이다. 클래스를 선언하고 해당 클래스의 인스턴스를 함수에 전달하는 대신 함수를 직접 전달할 수 있다. __

아래 에를 살펴보자.

```kotlin
 button.setOnClickListener(object: OnClickListener {
            override fun onClick(v: View) {
                println("I was clicked!")
            }
})
```

이와 같은 객체를 선언하는데 필요한 장황함은 여러번 반복되면 짜증이 난다. 동작(클릭 시 수행해야 하는 작업)만을 표현하는 표기법을 사용하면 람다를 사용하여 앞의 스니펫을 다시 작성할 수 있으므로 중복 코드를 제거할 수 있다.

```kotlin
button.setOnClickListener {
            println("I was clicked!")
}
```

이 `Kotlin` 코드는 익명 객체를 사용하는 것과 동일한 작업을 수행하지만 더 간결하고 가독성이 높다. 

### 5.1.2 람다 및 컬렉션

좋은 프로그래밍 스타일의 주요 원칙 중 하나는 코드의 중복을 피하는 것이다. 람다를 통해 `Kotlin`은 컬렉션 작업을 위한 강력하고 편리한 표준 라이브러리를 제공한다.

```kotlin
data class Person(val name: String, val age: Int)
```

사람 목록이 있는데 그중 가장 나이가 많은 사람을 찾아야 한다고 가정해 보겠다. 두 개의 중간 변수, 즉 최대 나이를 저장하는 변수와 이 나이의 첫 번째 발견자를 저장하는 변수를 도입한 다음 목록을 반복하여 이 변수를 업데이트할 수 있다.

```kotlin
fun findTheOldest(people: List<Person>) {
    var maxAge = 0
    var theOldest: Person? = null
    for (person in people) {
        if (person.age > maxAge) {
            maxAge = person.age
            theOldest = person
} }
    println(theOldest)
}

fun main() {
    val people = listOf(Person("Alice", 29), Person("Bob", 31))
    findTheOldest(people)
    // Person(name=Bob, age=31)
}
```

경험이 충분하다면 이러한 루프를 꽤 빠르게 만들 수 있다. 하지만 여기에는 보일러 플레이트 코드가 상당히 많기 때문에 실수하기 쉽다. 

`Kotlin`에는 더 좋은 방법이 있다. 다음 그림과 같이 표준 라이브러리의 함수를 사용하면 된다.

```kotlin
fun main() {
    val people = listOf(Person("Alice", 29), Person("Bob", 31))
	println(people.maxByOrNull { it.age })
    // Person(name=Bob, age=31)
}
```

최대 엘리먼트를 찾기 위해 비교해야 할 값을 지정하는 함수로, 모든 컬렉션에서 호출 할수 있으며 하나의 인수를 받는다. 중괄호 `{ it.age }`로 묶인코드는 이`selector` 로직을 구현하는 람다로, 컬렉션 요소를 인수로 받아 비교할 값을 반환한다. 람다는 하나의 인수(컬렉션 항목)만 받고 명시적인 이름을 지정하지 않으므로 암시적 이름인 `it`을 사용하여 참조한다.

```kotlin
people.maxByOrNull(Person::age)
```

람다가 함수나 프로퍼티에 위임만 하는 경우에는 메모리 참조로 대체할 수 있다.

우리가 일반적으로 컬렉션으로 하는 대부분의 작업은 람다나 멤버 참조를 사용 하는 라이브러리 함수로 간결하게 표현할 수 있다. 결과 코드는 훨씬 짧고 이해하기 쉬우며, 루프 기반 코드보다 의도를 더 명확하게 전달(즉, 코드가 달성하려는 목적)하는 경우가 많다. 

### 5.1.3 람다 표현식 구문

앞서 언급했듯이 람다는 값으로 전달할 수 있는 작은 동작 조각을 의미한다. 람다는 독립적으로 선언하여 변수에 저장할 수도 있다. 하지만 함수에 전달할 때 직접 선언하는 경우가 더 많다. 

![](https://velog.velcdn.com/images/cksgodl/post/2dd95884-d071-4360-aafa-15a6f43294de/image.png)

- 람다 표현식 구문 : 람다는 항상 중괄호로 둘러싸여 있으며 여러 매개변수를 지정하고 실제 논리를 포함하는 람다의 본문을 제공한다. 

화살표는 람다 본문에서 인수 목록을 구분한다. 람다 식을 변수에 저장한 다음 이 변수를 일반 함수처럼 취급할 수 있다.

```kotlin
fun main() {
	val sum = { x: Int, y: Int -> x + y }
	println(sum(1, 2))  // 3
}
```

함수에 여러 개의 인수가 있고 마지막 인수만 람다인 경우에 람다를 괄호 밖에 두는 것이 `Kotlin`에서 좋은 스타일로 간주된다. 두 개 이상의 람다를 전달하려는 경우 하나 이상의 람다를 괄호 밖으로 이동할 수 없으므로 일반적으로 모든 람다를 괄호 안에 유지하는 것이 좋다.

```kotlin
people.maxByOrNull { p: Person -> p.age } 
people.maxByOrNull { p -> p.age }
```

지역 변수와 마찬가지로 람다 매개변수의 유형을 유추할 수 있는 경우 명시적으로 지정 할 필요가 없다. 컴파일러는 `Person` 객체 컬렉션에서 `maxByorNull`을 호출한다는 것을 알고 있으므로 람다 매개변수의 유형도 `Person`이라는 것을 이해할 수 있다.

### 5.1.4 범위내변수액세스

함수에서 익명 내부 클래스를 선언하면 클래스 내부에서 해당 함수의 매개변수와 지역 변수를 참조할 수 있다는 것을 알고 있을 것이다. 람다를 사용하면 똑같은 작업을 수행 할 수 있다. 

__함수에서 람다를 사용하면 해당 함수의 매개변수와 람다 앞에 선언된 로컬 변수에 액세스할 수 있다__

```kotlin
fun printMessagesWithPrefix(messages: Collection<String>, prefix: String) { 
	messages.forEach {
		println("$prefix $it")
    }
}

fun main() {
    val errors = listOf("403 Forbidden", "404 Not Found")
    printMessagesWithPrefix(errors, "Error:")
    // Error: 403 Forbidden
    // Error: 404 Not Found
}
```

![](https://velog.velcdn.com/images/cksgodl/post/ab1e91ae-eb83-4c8d-b73c-6359f0df25fd/image.png)

`Kotlin`과 `Java`에서 람다를 사용할 때 한 가지 중요한 차이점은 `Kotlin`에서는 최종 변수에 액세스하는 데만 제한되지 않고 람다 내에서 변수를 수정할 수도 있다는 점이다. 

```kotlin
fun printProblemCounts(responses: Collection<String>) {
	var clientErrors = 0
	var serverErrors = 0
	responses.forEach {
    	if (it.startsWith("4")) {
        	clientErrors++
    	} else if (it.startsWith("5")) {
        	serverErrors++
	} 
}
    println("$clientErrors client errors, $serverErrors server errors")
}

fun main() {
    val responses = listOf("200 OK", "418 I'm a teapot",
                           "500 Internal Server Error")
    printProblemCounts(responses)
    // 1 client errors, 1 server errors
}
```

보시다시피 `Kotlin`에서는 람다에서 최종 변수가 아닌 변수에 액세스 및 수정할 수 있다. 이 예제에서 접두사, 클라이언트 오류, 서버 오류와 같이 람다에서 액세스하는 외부 변수는 람다에서 캡처한 것이다.

기본적으로 로컬 변수의 수명은 변수가 선언된 함수에 의해 제한된다는 점에 유의하라. 그러나 람다에 의해 캡처되면 이 변수를 사용하는 코드를 나중에 저장하고 실행할 수 있다.`final` 변수를 캡처하면 해당 값은 해당 변수를 사용하는 람다 코드와 함께 저장된다. `final` 변수가 아닌 변수의 경우 값을 변경할 수 있는 특수 래퍼로 값을 둘러싸고 래퍼에 대한 참조가 람다와 함께 저장된다.

> 변경 가능한 변수 캡처하는 구현 세부정보
> 
> `Java`에서는 `final` 변수만 캡처할 수 있다. 변경 가능한 변수를 캡처하려면 다음 기법 중 하나를 사용할 수 있다. 변경 가능한 값을 저장할 요소의 배열을 선언하거나 변경 가능한 참조를 저장하는 래퍼 클래스의 인스턴스를 생성하는 것이다. `Kotlin`에서 이 기법을 명시적으로 사용하는 경우 코드는 다음과 같다:
```kotlin
class Ref<T>(var value: T)
fun main() {
    val counter = Ref(0)
    val inc = { counter.value++ }
}
```
> 실제 코드에서는 이러한 래퍼를 만들 필요가 없다. 대신 변수를 직접 변경할 수 있다:
>
> 첫 번째 예제는 두 번째 예제가 내부적으로 어떻게 작동하는지 보여준다. 최종 변수(`val`)를 캡처할 때마다 `Java`에서와 같이 해당 값이 복사된다. 가변 변수 (`var`)를 캡처하면 그 값은 `Ref` 클래스의 인스턴스로 저장된다. `Ref` 변수는 최종 변수이므로 쉽게 캡처할 수 있는 반면, 실제 값은 필드에 저장되며 람다에서 변경할 수 있다.

중요한 주의 사항은 람다가 이벤트 핸들러로 사용되거나 비동기적으로 실행되는 경우, 로컬 변수에 대한 수정은 람다가 실행될 때만 발생한다는 것이다.

```kotlin
fun tryToCountButtonClicks(button: Button): Int {
    var clicks = 0
    button.onClick { clicks++ }
    return clicks
}
```

이 함수는 항상 0을 반환한다. 온클릭 핸들러가 클릭 수를 수정하더라도 함수가 반환된 후에 온클릭 핸들러가 호출되기 때문에 수정 사항을 관찰할 수 없다. 함수를 올바르 게 구현하려면 클릭 수를 로컬 변수가 아닌 함수 외부에서 액세스할 수 있는 위치(예: 클래스의 속성)에 저장해야 한다.

### 5.1.5 멤버 참조

람다를 사용하여 코드 블록을 함수의 매개변수로 전달하는 방법을 살펴보았지만, 매개 변수로 전달해야 하는 코드가 이미 함수로 정의되어 있는 경우에는 어떻게 해야 할까? 물론 해당 함수를 호출하는 람다를 전달할 수 있지만 그렇게 하는 것은 다소 중복됩니다.

`Kotlin`에서는 `Java 8`과 마찬가지로 함수를 값으로 변환하면 그렇게 할 수 있다. 이를위해`::` 연산자를 사용한다.

```kotlin
val getAge = Person::age
```

이 표현식을 멤버 참조라고 하며, 정확히 하나의 메서드를 호출하는 함수 값을 만들기 위한 짧은 구문을 제공한다.(프로퍼티도 엑세스 가능) 이중콜론은 클래스 이름과 참조해야 하는 멤버 이름(메서드 또는 속성)을 구분 한다.

![](https://velog.velcdn.com/images/cksgodl/post/c7aa5cc2-a747-419e-ab92-740bf15454fb/image.png)

```kotlin
val getAge = Person::age
val getAge = { person: Person -> person.age } // 동일
```

함수를 참조하든 프로퍼티를 참조하든 관계없이 멤버 참조에서 이름 뒤에 괄호를 넣으면 안 된다는 점에 유의하라. 결국 함수를 호출하는 것이 아니라 함수에 대한 참조로 작업하는 것이기 때문이다.

멤버 참조는 해당 함수 또는 프로퍼티를 호출하는 람다와 동일한 유형을 가지므로 두 가지를 서로 바꿔서 사용할 수 있다

최상위 수준에서 선언된 함수(클래스의 멤버가 아닌)에 대한 참조도 가질 수 있다.

```kotlin
fun salute() = println("Salute!")
fun main() {
	run(::salute) 
}
```

이 경우 클래스 이름을 생략하고 `::` 로 시작한다. 멤버참조 `::salute`를 라이브러리 함수 `run`에 인자로 전달하면 해당 함수가 연관 함수를 호출한다.

람다가 여러 매개변수를 받는 함수에 위임할 때 멤버 참조를 제공하면 매개변수 이름과 그 유형을 반복하지 않아도 되므로 특히 편리하다.

```kotlin
val action = { person: Person, message: String -> 	
	sendEmail(person, message) 
}
val nextAction = ::sendEmail
```

생성자 참조를 사용하여 클래스의 인스턴스를 생성하는 작업을 저장하거나 연기할 수
있다. 생성자 참조는 이중 콜론 뒤에 클래스 이름을 지정하여 형성된다.

```kotlin
data class Person(val name: String, val age: Int)

fun main() {
    val createPerson = ::Person
    val p = createPerson("Alice", 29)
    println(p)
    // Person(name=Alice, age=29)
}
```

### 5.1.6 바인딩된 호출 가능한 참조

지금까지 멤버 참조는 항상 클래스의 멤버를 가르켰다. 바인딩된 호출 가능 참조를 사용하면 동일한 멤버 참조 구문을 사용하여 특정 객체 인스턴스의 메서드에 대한 참조를 캡처할 수 있다. 

아래 예제를 보자.

```kotlin
fun main() {
    val seb = Person("Sebastian", 26)
    val personsAgeFunction = Person::age // 주어진 사람의 나이를 반환하는 참조
    println(personsAgeFunction(seb)) // Person 객체를 인수로 받는다.
    // 26
    val sebsAgeFunction = seb::age
    println(sebsAgeFunction()) // 특정 사람의 나이를 반환하는 바인딩 된 멤버 참조
    // 26
}
```

![](https://velog.velcdn.com/images/cksgodl/post/4c4402f2-4391-4c14-a5f7-87902c60af69/image.png)

## 5.2 Java 함수 인터페이스 사용: 단일 추상 메서드

이미 `JVM` 에코시스템에는 `Kotlin`으로 작성된 많은 라이브러리가 있으며, 이러한 라이브러리는 `Kotlin`의 람다를 직접 사용할 수 있다. 하지만 `Kotlin` 프로젝트에서 `Java`로 작성된 라이브러리를 사용하고 싶을 가능성이 높다. 좋은 소식은 `Kotlin` 람다가 `Java API`와 완벽하게 상호 운용된다는 것이다. 이 섹션에서는 이것이 어떻게 작동하 지 자세히 살펴보겠다.

`Java` 버전에 따라 `onClickListener` 인터페이스를 구현하는 것은 상당히 복잡할 수 있다. `Java 8` 이전 버전에서는 익명 클래스의 인스턴스를 새로 생성하여 전달해야 했다.

```kotlin
button.setOnClickListener { 
	println("I was clicked!")
}

/* Java */
public interface OnClickListener {
	void onClick(View v);
}

/* Java */
public class Button {
	public void setOnClickListener(OnClickListener l) { ... 	}
}

/* Before Java 8 */
button.setOnClickListener(new OnClickListener() {
	@Override
    public void onClick(View v) {
    /* ... */ }
}
```

`Kotlin`에서는 람다를 전달하기만 하면 된다:

```kotlin
button.setOnClickListener { view -> /* ... */ }
```

![](https://velog.velcdn.com/images/cksgodl/post/ab704f1e-a9d6-4bdf-bceb-34dd6bbb0106/image.png)

이는 `onClickListener` 인터페이스에 추상 메서드가 하나만 있기 때문에 작동한다. 이러한 인터페이스를 함수형 인터페이스 또는 단일 추상 메서드(`SAM`) 인터페이스라고 한다. 

`JavaAPI`는 실행 및 호출 기능과 같은 함수형 인터페이스와 이를 사용하는 메서드로 가득하다. `Kotlin`에서는 함수형 인터페이스를 매개 변수로 사용하는 `Java` 메서드를 호출할 때 람다를 사용할 수 있으므로 `Kotlin` 코드가 깔끔하고 관용적인 상태를 유지 할 수 있다. 

### 5.2.1 Java 메서드에 람다를 매개변수로 전달하기

함수형 인터페이스를 기대하는 모든 `Java` 메서드에 람다를 전달할 수 있다.

```kotlin
/* Java */
void postponeComputation(int delay, Runnable computation);

postponeComputation(1000) { println(42) }
```

"Runnable의 인스턴스"라고 할 때, 이는 "Runnable"을 구현하는 익명 클래스의 인스턴스"를 의미한다. 컴파일러가 이를 생성하고 람다를 단일 추상 메서드(이 경우 실행 메서드)의 본문으로 사용한다.

이는 아래처럼 사용할 수도 있다.

```kotlin
postponeComputation(1000, object : Runnable {
    override fun run() {
        println(42)
    }
})
```

하지만 차이가 있다. 객체를 명시적으로 선언하면 호출할 때마다 새 인스턴스가 생성된다. 람다를 사용하면 상황이 달라진다.

```kotlin
postponeComputation(1000) { println(42) } // 전체 프로그램에 대해 하나의 런너블 인스턴스가 생성
```
정의된 함수의 변수에 액세스하지 않으면 해당 익명 클래스 인스턴스가 호출 간에 재사용된다

__람다가 주변 범위에서 변수를 캡처하면 더 이상 모든 호출에 동일한 인스턴스를 재사용 할 수 없다. 이 경우 컴파일러는 모든 호출에 대해 새 객체를 생성하고 캡처된 변수의 값을 해당 객체에 저장한다.__

```kotlin
fun handleComputation(id: String) {
    postponeComputation(1000) { // 각 핸들컴퓨팅 호출에 대해 Runnable의 새 인스턴스를 생성
        println(id) // 람다에서 변수 ID를 캡처
    }
}
```

람다를 위한 익명 클래스와 이 클래스의 인스턴스를 만드는 방법에 대한 설명은 함수형 인터페이스를 기대하는 `Java` 메서드에는 유효하지만 `Kotlin` 확장 메서드를 사용하는 컬렉션 작업에는 적용되지 않는다는 점에 유의하라. 

인라인으로 표시된 `Kotlin` 함수에 람다를 전달하면 익명 클래스가 생성되지 않는다. 그리고 대부분의 콜렉션 라이브러리 함수는 인라인으로 구현되어 있다.

지금까지 살펴본 것처럼 대부분의 경우 람다를 함수형 인터페이스의 인스턴스로 변 환하는 작업은 사용자의 노력 없이 자동으로 이루어진다. 하지만 명시적으로 변환을 수행해야 하는 경우도 있다. 

### 5.2.2 SAM 생성자: 람다를 함수형 인터페이스로의 명시적 변환

__`SAM` 생성자는 단일 추상 메서드를 사용하여 람다를 인터페이스의 인스턴스로 명시적 으로 변환할 수 있는 컴파일러 생성 함수이다.__

컴파일러가 변환을 자동으로 적용하지 않는 컨텍스트에서 이 함수를 사용할 수 있다. 예를 들어 함수형 인터페이스의 인스턴스를 반환하는 메서드가 있는 경우 람다를 직접 반환할 수 없고 `SAM` 생성자로 래핑해야 한다.

```kotlin
fun createAllDoneRunnable(): Runnable {
 	return Runnable { println("All done!") }
}

fun main() {
	createAllDoneRunnable().run()
    // All done!
}
```

`SAM` 생성자의 이름은 기본 함수형 인터페이스의 이름과 동일하다. `SAM` 생성자는 단일 인자(람다)를 받는다. `SAM` 생성자는 값을 반환하는 것 외에도 람다에서 생성된 함수형 인터페이스 인스턴스를 변수에 저장해야 할 때 사용된다.

```kotlin
val listener = OnClickListener { view -> // 람다로 SAM 생성자를 호출
    val text = when (view.id) {
        button1.id -> "First button"
        button2.id -> "Second button"
        else -> "Unknown button"
	}
    toast(text)
}
button1.setOnClickListener(listener)
button2.setOnClickListener(listener)
```

리스너는 어떤 버튼이 클릭의 원인이었는지 확인하고 그에 따라 동작한다. 클릭 리스너를 구현하는 객체 선언을 사용하여 리스너를 정의할 수도 있지만 `SAM` 생성자를 사용하면 보다 간결한 옵션을 사용할 수 있다.

## 5.3 Kotlin에서 SAM 인터페이스 정의하기: fun interfaces

`Kotlin`에서는 함수형 인터페이스를 사용해야 하는 동작을 표현하기 위해 함수형을 사용 할 수 있는 경우가 많다.

`Kotlin`의 함수형 인터페이스는 정확히 하나의 추상 메서드를 포함하지만 추상 메서드가 아닌 여러 개의 추가 메서드를 포함할 수도 있다. 이를 통해 함수 유형의 시그니처에 넣을 수 없는 더 복잡한 구조를 표현하는 데 도움이 될 수 있다.

```kotlin
fun interface IntCondition {
    fun check(i: Int): Boolean
    fun checkString(s: String) = check(s.toInt())
    fun checkChar(c: Char) = check(c.digitToInt())
}

fun main() {
    val isOdd = IntCondition { it % 2 != 0 }
    println(isOdd.check(1))
    // true
    println(isOdd.checkString("2"))
    // false
    println(isOdd.checkChar('3'))
    // true
}
```

위 예제에서는 추상 메서드 `check`를 사용하여 `IntCondition`이라는 함수형 인터페이스를 정의한다. 매개변수를 정수로 변환한 후 `check`를 호출하는 `checkString`이라는 비추상 메서드를 추가로 정의한다. `Java SAM`과 마찬가지로 `SAM` 생성자를 사용하여 `check`의 구현을 지정하는 람다로 인터페이스를 인스턴스화한다.

함수가 `fun interfaces`로 정의된 유형의 매개변수를 받아들이는 경우, 람다 구현을 직접 제공하거나 람다에 대한 참조를 전달할 수도 있으며, 이 두 가지 모두 인터페이스 구현을 동적으로 인스턴스화한다.

```kotlin
fun checkCondition(i: Int, condition: IntCondition): Boolean {
    return condition.check(i)
}

fun main() {
	checkCondition(1) { it % 2 != 0 }  // true
	val isOdd:(Int) -> Boolean = { it%2!=0 }
	checkCondition(1, isOdd) // true
}
```
다음 예제에서는 이전에 정의한 대로 `IntCondition`을 받는 `checkCondition`함수를 정의하고 있다. 그런 다음 람다를 직접 전달하거나 올바른 타입의 함수((Int)->부 울)에 대한 참조를 전달하는 등 다양한 방법으로 해당 함수를 호출할 수 있다.


#### fun interface를 갖춘 깔끔한 Java 호출 

`Java` 코드와 `Kotlin` 코드 모두에서 사용될 것으로 예상되는 코드를 작성하는 경우 `fun interface`를 사용하면 `Java`호출의 깔끔함을 향상 시킬 수 있다. `Kotlin`함수유형은 일반 유형이 매개변수와 반환 유형인 개체로 변환된다. 아무것도 반환하지 않는 함수의 경우 `Kotlin`은 `Java`의 `void`에 대한 아날로그로 `Unit`을 사용한다

즉, `Java`에서 이러한 `Kotlin` 함수 유형을 호출할 때 호출자는 명시적으로 `Unit.INSTANCE`를 반환해야 한다. `fun interface`를 사용하면 이러한 요구 사항이 제거되어 호출 사이트가 더 간결해진다. 

```kotlin
fun interface StringConsumer {
    fun consume(s: String)
}
fun consumeHello(t: StringConsumer) {
    t.consume("Hello")
}
fun consumeHelloFunctional(t: (String) -> Unit) {
    t("Hello")
}
```

`Java`에서 사용하는 경우 `fun interface`를 사용하는 함수의 변형은 간단한 람다로 호출할 수 있지만, `Kotlin` 함수형을 사용하는 변형은 람다가 `Kotlin`의 `Unit.INSTANCE`를 명시적으로 반환해야 한다:

```java
public class MyApp {
    public static void main(String[] args) {
        /* Java */
        MainKt.consumeHello(s -> System.out.println(s.toUpperCase()));
        MainKt.consumeHelloFunctional(s -> {
            System.out.println(s.toUpperCase());
            return Unit.INSTANCE;
	}); }
}
```

## 5.4 수신기가 있는 람다 : `with`, `apply` 및 `also`

이 섹션에서는 `Kotlin` 표준 라이브러리의 `with`, `apply` 및 기타 함수에 대해 설명한다. 이러한 함수는 편리하며 선언 방법을 이해하지 못하더라도 다양한 용도로 사용할 수 있다. 

- with

이름을 반복하지 않고 동일한 객체에 대해 여러 작업을 수행하는 데 사용 할 수 있는 특수문이다.

```kotlin
// with X
 fun alphabet(): String {
 		val result = StringBuilder()
        for (letter in 'A'..'Z') {
        	result.append(letter)
		}
        result.append("\nNow I know the alphabet!")
        return result.toString()
	}

fun main() {
	println(alphabet())
    // ABCDEFGHIJKLMNOPQRSTUVWXYZ
    // Now I know the alphabet!
}

// with O
fun alphabet(): String {
    val stringBuilder = StringBuilder()
    return with(stringBuilder) {
        for (letter in 'A'..'Z') {
            this.append(letter)
		}
        this.toString()
    }
}
```

`with` 함수는 첫 번째 인수를 두 번째 인자로 전달된 람다의 리시버로 변환한다. 명시적인 `this` 참조를 통해 이 리시버에 액세스할 수 있다. 또는 이 참조의 일반적인 경우`with`가 참조를 생략하고 추가 한정자없이 이 값의 메서드나 프로퍼티에 액세스할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/23170d8c-883c-4cb3-b79e-ecd737132ab5/image.png)


> 수신기 및 확장기능이 있는 람다
>
> 확장 함수는 어떤 의미에서 수신자가 있는 함수라는 점에 유의하라.
![](https://velog.velcdn.com/images/cksgodl/post/f6a4511d-2d5a-4e95-a5a1-7ce038bd6aeb/image.png)

최종적으로 위 코드를 리팩터링하면 다음과 같다.

```kotlin
fun alphabet() = with(StringBuilder()) {
    for (letter in 'A'..'Z') {
        append(letter)
    }
    append("\nNow I know the alphabet!")
    toString()
}
```

### 5.4.2 객체 초기화 및 구성을 위한 `apply`

`apply` 함수는 `with`와 거의 동일하게 작동하지만, 가장 큰 차이점은 apply는 항상 인자로 전달된 객체(즉,수신자객체)를 반환 한다는점이다. 

```kotlin
 fun alphabet() = StringBuilder().apply {
 	for (letter in 'A'..'Z') {
 		append(letter)
 	}
 	append("\nNow I know the alphabet!")
}.toString()
```

이 기능이 유용한 많은 경우 중 하나는 객체의 인스턴스를 만들 때 일부 속성을 즉시 초 기화해야 하는 경우이다. `Java`에서는 일반적으로 별도의 빌더 개체를 통해 이 작업을 수행하지만, `Kotlin`에서는 객체가 정의된 라이브러리의 특별한 지원 없이도 모든 객체에서 `apply`을 사용할수있다.


### 5.4.3 객체로 추가 작업 수행 `also`

`apply`와 마찬가지로, 또한 함수를 사용하여 수신자 객체를 가져와서 작업을 수행한
다음 수신자 객체를 반환할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/ed07bc1c-183c-4b9f-93e3-1884715a197c/image.png)

```kotlin
fun main() {
    val fruits = listOf("Apple", "Banana", "Cherry")
    val uppercaseFruits = mutableListOf<String>()
    val reversedLongFruits = fruits
        .map { it.uppercase() }
        .also { uppercaseFruits.addAll(it) }
        .filter { it.length > 5 }
        .also { println(it) }
        .reversed()
    // [BANANA, CHERRY]
    println(uppercaseFruits)
    // [APPLE, BANANA, CHERRY]
    println(reversedLongFruits)
    // [CHERRY, BANANA]
}
```

## 요약
- 람다를 사용하면 코드 덩어리를 함수의 인수로 전달할 수 있으므로 일반적인
코드 구조를 쉽게 추출할 수 있다.
- `Kotlin`에서는 괄호 밖의 함수에 람다를 전달하여 코드를 깔끔하고 간결하게
만들 수 있다.
- 람다가 하나의 매개변수만 받는 경우, 암시적 이름인 it으로 람다를 참조할 수
있다. 이렇게 하면 짧고 간단한 람다로 유일한 람다 매개변수의 이름을 명시적 으로 지정하는 수고를 덜 수 있다.
- __람다는 외부 변수를 캡처할 수 있다.__
- 함수이름앞에:: 를붙여 메서드, 생성자 및 프로퍼티에 대한 참조를 만들 수 있다. 
- 단일 추상 메서드(일명 SAM 인터페이스)로 인터페이스를 구현하려면 인터페이스를 구현하는 객체를 명시적으로 생성하는 대신 람다를 전달하기만 하면 된다.
- 수신자가 있는 람다는 특수한 수신자 객체에서 메서드를 직접 호출할 수 있는 람다이다. 
- 표준 라이브러리 함수를 사용하면 객체에 대한 참조를 반복하지 않고도 동일한 객체에서 여러 메서드를 호출할 수 있다. apply를 사용하면 빌더 스타일의 API를 사용하여 객체를구조화하고 초기화할 수 있다. 또한 객체로 추가 작업을수행할 수도 있다.

