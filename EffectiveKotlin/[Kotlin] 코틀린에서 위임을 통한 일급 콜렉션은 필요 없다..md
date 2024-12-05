[우테코-프리코스-3주차](https://velog.io/@cksgodl/%EC%9A%B0%ED%85%8C%EC%BD%94-%EC%95%88%EB%93%9C%EB%A1%9C%EC%9D%B4%EB%93%9C-3%EC%A3%BC%EC%B0%A8-%ED%86%BA%EC%95%84%EB%B3%B4%EA%B8%B0) 때 일급콜렉션에 간단히 공부하고 사용하는 경험을 했었다. 

해당 내용을 복기하자면 다음과 같다.

# 일급콜렉션이란?

[일급 컬렉션을 사용하는 이유](https://tecoble.techcourse.co.kr/post/2020-05-08-First-Class-Collection/)

Collection을 Wrapping하면서 그 외 다른 멤버 변수가 없는 상태를 일급 컬렉션이라고 한다. 

자바에서의 일급 콜렉션의 선언은 다음과 같다.
```java
public class Lotto {
    // 멤버 변수가 하나밖에 없다는게 중요!!
    private List<LottoNumbers> numbers;

    public Lotto(List<LottoNumbers> numbers) {
        this.numbers = numbers;
    }
}
```

코틀린에서는 좀 더 간단하게 선언할 수 있다.
```kotlin
class Lotto(private val numbers: List<LottoNumber>) : List<LottoNumber> by numbers {
	
}
```
위의 소스에서는 Lotto객체의 타입을 `List<LottoNumber>`으로 상속받고 인자로 받은 numbers를 이용하여 프로퍼티 위임(by)을 받은 것을 볼 수 있다.

> 코틀린의 클래스는 기본적으로 상속할 수 없도록 정의되어 있다. (Open 어노테이션을 붙여야함) 이때 위임을 사용하면 상속하는 클래스의 모든 기능을 구현하는 동시에 추가 기능도 구현할 수 있다. 실제로 상속받는건 아님!
위임 : 클래스의 객체가 단순히 다른 클래스의 객체를 사용만 해야 한다면 델리게이션을 사용해라.

이렇게 위임받으면 포워딩 메서드들을 자동으로 생성할 수 있다.
`List<LottoNumber>`콜렉션에 대한 모든 확장함수가 Lotto에서도 제공된다.

![](https://velog.velcdn.com/images/cksgodl/post/acf9d819-73ec-4a53-bfad-05cc30b5c4e6/image.png)

#### 일급 콜렉션을 사용함으로써

* 비지니스에 종속적인 자료구조
해당 로또에서는 모든 로또 번호에 대한 도메인 로직, 밸리데이션 처리 등의 기능을 한 모델에서 수행할 수 있다. **특정 조건으로 만들 수 있는 자료구조를 생성하는 것이다.**

* MutableList가 아닌 List를 사용함으로써 Collection의 불변성을 보장

* 이름이 있는 컬렉션으로 가독성 증가

```kotlin
// 멤버 변수가 numbers밖에 없다.
class Lotto(private val numbers: List<LottoNumber>) : List<LottoNumber> by numbers {
    init {
        checkValidation()
    }

    override fun toString(): String {
        return numbers.toString()
    }

    fun containsNumber(number: Int) = numbers.contains(LottoNumber.valueOf(number))

    private fun checkValidation() {
        require(numbers.size == LOTTO_LENGTH) {
            LOTTO_LENGTH_MUST_SIX_TEXT
        }
        require(numbers.distinct().size == LOTTO_LENGTH) {
            LOTTO_NOT_DUPLICATE_TEXT
        }
    }

}
```

# 코틀린에 위임패턴의 일급콜렉션이 필요한가?

하지만 이렇게 내가 정의한 위임패턴을 적용한 일급콜렉션이 과연 효율적인가?에 대해 의문점이 생겼다. 

일단 `first class collection kotlin`에 대한 구글 검색 결과가 하나도 없다. 영어로된 문서라도 하나 나오면 좋겠는데 아무런 문서가 존재하지 않는다..! 🤔 무엇인가 잘못 사용하고 있음을 깨달았고(효율적인 사용방법 이라면 지금껏 다른 사람들이 사용하지 않을 이유가 없음) 왜 사용하지 않는지 정리해 볼려고 한다.

```kotlin
class Students(private val students: List<Student>) : List<Student> by students {

    fun findByName(name: String): Student {
        return students.find { it.name == name } ?: throw IllegalArgumentException("그런 학생은 없어요~")
    }
}

data class Student(
    val name: String,
    val id: Int,
    val grade: String
)
```
`Students`는 학생 리스트를 위임받은 일급 콜렉션이다.
`Student`는 데이터 클래스로 이름, 학번, 성적을 저장할 수 있다.

비지니스에 종속적인 자료구조를 만들기 위해 `List<Student>`만을 위한 함수 `findByName`을 정의했다.

### 잘못된 점 #1

by 위임패턴을 통한 클래스 선언은 `List<Student>`의 모든 함수를 위임받는다. 이는 즉 객체의 생성 비용이 상당하다는 것을 의미한다. 



```java
public final class Students implements List, KMappedMarker {
   private final List students;

   @NotNull
   public final Student findByName(@NotNull String name) {
      // ...
   }

   public Students(@NotNull List students) {
      Intrinsics.checkNotNullParameter(students, "students");
      super();
      this.students = students;
   }

   public int getSize() {
      return this.students.size();
   }

   // $FF: bridge method
   public final int size() {
      return this.getSize();
   }

   public boolean contains(@NotNull Student element) {
      Intrinsics.checkNotNullParameter(element, "element");
      return this.students.contains(element);
   }
	
    // ...

}
```

`Students`클래스를 자바로 디컴파일한 코드이다. 실제론 250줄이 넘는데 정말 일부만을 가져왔다. 이처럼 일급 콜랙션을 만든다고 한다면 정말 많은 비용이 소모되며 간단한 비즈니스 로직 한, 두개를 위해 이러한 클래스를 만드는 것은 옳지 않다.

### 대안 #1

위임하지 않는다. 내가 필요한 비즈니스 로직만 해당로직에 작성하여 객체 생성 비용을 줄인다.

```kotlin
class Students(private val students: List<Student>) {

    fun findByName(name: String): Student {
        return students.find { it.name == name } ?: throw IllegalArgumentException("그런 학생은 없어요~")
    }
    
    // ...
}
```
하지만 이러한 방식도 `Students`라는 객체를 생성해야 하며, 이는 객체가 차지할 공간, 이에 대한 레퍼런스를 생성하는 등의 추가적인 작업이 필요하게 된다.

### 대안 #2
탑레벨 함수를 정의하여 사용하는 것이다. 한정자 `private`을 활용하여 외부에서 이 함수에 대해 가릴 수 있을 뿐만 아니라 비즈니스 로직을 추출할 수있으며, 디컴파일되는 소스도 정말로 적다.

```kotlin
private fun List<Student>.topFuncFindByName(name: String): Student {
    return find { it.name == name } ?: throw IllegalArgumentException("그런 학생은 없어요~")
}
```
```java
private static final Student topFuncFindByName(@NotNull List $this$topFuncFindByName, @NotNull String name) {
	// ..
}
```

### 잘못된 점 #2

불변성을 제공하지 않는다.

```kotlin
class Students(private val students: List<Student>) {

    fun getLength() = students.size

    fun findByName(name: String): Student {
        return students.find { it.name == name } ?: throw IllegalArgumentException("그런 학생은 없어요~")
    }
}
```
위임 패턴을 사용하지 않으니 `students`콜렉션에 대한 `getLength()`도 수동적으로 구현해야한다. -> 이는 코틀린의 장점인 가독성을 해치는 나쁜행동 😡
```kotlin
val studentList = mutableListOf(
    Student("해찬", 2018125054, "A"),
    Student("승현", 2018125002, "B"),
    Student("현섭", 2018125023, "C")
)
val students = Students(studentList)
println(students.getLength()) // 3
studentList.add(Student("보현", 2018125033, "A"))
println(students.getLength()) // 4
```

분명 `Students`클래스는 `immutable`한 콜렉션으로 선언되어 있는데 `mutable`한 객체를 아규먼트로 집어 넣고 내용을 추가하면 그 길이가 바뀐다. 

> List는 MutableList의 부모 타입이기 때문에 가능

이처럼 분명 변하지 않을 것이라고 기대하던 리스트의 길이가 변화할 수 있다. 예기치 못한 오류가 발생 가능

### 문제점 #3

테코블 사이트에서는 일급 콜렉션을 필요한 값만 반환하는 별도의 메소드만 만들어 사용하고 있다고한다.

> 저 역시 일급컬렉션에 필요한 값만 반환하는 별도의 메소드들을 만들어서 사용하고 있습니다.
(컬렉션 그대로 반환하지 않고, 외부에선 컬렉션 내부 필드에 단독 접근은 불가능한 형태)
생성자로 받은 컬렉션값을 그대로 반환하는 기능은 두지 않고, 가공된 값 or 목적에 맞는 값만 반환하는 형태로 구현하고 있습니다.

이것도 확장함수를 통해 해결할 수 있다.
* 특정 이름을 포함한 학생을 반환하는 함수
```kotlin
private fun List<Student>.getContains(name: String): List<Student> {
    return filter { it.name.contains(name) }
}
```


## 정리 

1. 코틀린에서는 해당 자료형(`List<Students>`)에 대한 추가 확장 함수를 만들 수 있기 때문에 이러한 일급 콜렉션은 필요하지 않다.

2. 생성된 일급콜렉션에 대한 불변성은 제공되지 않는다.

3. 필요한 값만 반환하는 별도의 메소드는 확장함수로 추출하라.

4. 만약 모든 콜렉션의 모든 기능이 필요하고, 해당 클래스에 대한 여러 로직이 중첩적으로 필요할 때는 위임패턴을 통한 일급콜렉션을 사용하자.