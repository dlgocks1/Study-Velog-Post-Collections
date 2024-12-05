
코틀린에서는 `lateinit`과 `lazy`를 통한 지연 생성을 지원한다. 이러한 지연생성을 사용하면 해당 프로퍼티가 사용될 때 프로퍼티가 만들어진다. 이렇게 생성 시점을 지연시킴으로 필요없는 프로퍼티가 지금 당장 만들어지는 비용, 시간을 절약할 수 있다.

```kotlin
class Student(private val name: String)

class School(private val name: String)

class SampleActivity {

    private val school = School("한국항공대학교") // 지금 당장 사용하는 게 아니라면 메모리 손해
    private lateinit var school: School // 생성을 지연한다.

}
```

기존 `java`소스를 코틀린으로 바꾸다보면 다음과 같은 소스를 자주 보게 될것이다.

```kotlin
private var sampleAdapter: SampleAdapter? = null

// ...

sampleAdapter = SampleAdapter(/* */)
```
자바의 참조객체는 `null`에 대한 접근이 가능하여, 언제든 `null`로 표현할 수 있지만 코틀린의 경우는 기본적으로 `null`이 허용되지 않는다.(`?`를 붙이거나) 그래서 먼저 `null`로 초기화를 진행하고, 이후 생성을 하는 식으로 진행하는데 코틀린의 프로퍼티 위임 즉 `lateinit`과 `lazy`를 활용하면 이렇게 진행할 필요가 없다.

---



# Late-initialized properties and variables

[Late-initialized properties - kotlinlang.org](https://kotlinlang.org/docs/properties.html#late-initialized-properties-and-variables)

일반적으로 프로퍼티는 생성자에서 초기화되어야 한다. 하지만 종속성 주입또는 단위 테스트의 경우 초기화 시점을 변경할 수 있다. 이러한 방법을 사용하면 `null`로 초기화하여 초기 `null check`를 수행하지 않고 프로퍼티의 내용을 참조할 수 있다.

다음은 `lateinit`한정자를 활용하여 유닛테스트 코드이다.
`@setup` 어노테이션은 해당 테스트가 진행되기 전에 실행되고 여기서 초기화를 진행
```kotlin
public class MyTest {
    lateinit var subject: TestSubject

    @SetUp fun setup() {
        subject = TestSubject()
    }

    @Test fun test() {
        subject.method()  // dereference directly
    }
}
```

`lateinit`한정자를 사용하는데에 몇 가지 조건이 있다.

* var(mutable)에서만 사용이 가능하다.
	* var이기 때문에 언제든 초기화를 변경할 수 있다.
* 최상위 프로퍼티 및 변수에 사용할 수 없다.
* null을 통한 초기화를 할 수 없다.
* 변수에 대한 `setter/getter properties` 정의가 불가능하다.
* 원시타입에 대한 선언이 가능하다.
* 초기화를 하기 전에는 변수에 접근할 수 없다.

초기화되기 전에 lateinit 속성에 액세스하면 `lateinit property students has not been initialized` 예외가 발생한다.

해당 프로퍼티가 생성됐는지 확인하려면 `isInitialized`를 활용해 알 수 있다.
```kotlin
if (foo::bar.isInitialized) {
    println(foo.bar)
}
```

간단한 `lateinit`의 예로 다음 코드를 보자.

```kotlin
class Student(private val name: String) {
    init {
        println("학생 $name(이)가 생성됨")
    }
}

class School(private val name: String) {

    lateinit var students: MutableList<Student>

    init {
        println("학교 $name(이)가 생성됨")
    }

    fun addStudents(student: Student) {
        if (!this::students.isInitialized) {
            students = mutableListOf()
        }
        students.add(student)
    }

}

fun main() {
    val mySchool = School("항공대")
    mySchool.addStudents(Student("해찬"))
    mySchool.addStudents(Student("찬주"))
}
```

* 출력 결과
```js
학교 항공대(이)가 생성됨
학생 해찬(이)가 생성됨
학생 찬주(이)가 생성됨
```

코틀린은 JVM에서 돌아가는 언어이고, 그럼 해당 언어를 자바로 디컴파일하면 어떻게 사용되고 있을까 알아보자.

```kotlin
public final class School {
   public List students;

   @NotNull
   public final List getStudents() {
      List var10000 = this.students;
      if (var10000 == null) {
         Intrinsics.throwUninitializedPropertyAccessException("students");
      }

      return var10000;
   }

   public final void setStudents(@NotNull List var1) {
      Intrinsics.checkNotNullParameter(var1, "<set-?>");
      this.students = var1;
   }
}
```

`lateinit var students`는 초기 자바에서 `null`로 초기화를 진행한 후 다음과 같이 getter, setter가 구현된 상태로 디컴파일 된다. 여기서 확인해야 할 점은 만약 초기화가 진행되지 않은 상태라면 `throwUninitializedPropertyAccessException`를 던지는것을 알 수 있다.

```kotlin
   public final void addStudents(@NotNull Student student) {
      Intrinsics.checkNotNullParameter(student, "student");
      if (((School)this).students == null) {
         this.students = (List)(new ArrayList());
      }

      List var10000 = this.students;
      if (var10000 == null) {
         Intrinsics.throwUninitializedPropertyAccessException("students");
      }

      var10000.add(student);
   }
```

`addStudents`함수 에서도 this.students에 대한 null체크를 진행하여 `throwUninitializedPropertyAccessException`를 던진다. 이 lateinit 프로퍼티에 대한 `null`체크는 이 프로퍼티가 사용되는 모든 부분에서 확인하게 된다.

예를 들어 학생리스트를 받아와 모두 더하는 함수가 있을 때, (`addAll`을 활용하여 넣을 수 있지만, 일부로 포문으로 확인) 해당 프로퍼티에 대한 `null`체크를 포문마다 진행하는 것을 볼 수 있다. 
```kotlin
fun addStudentsAll(students: List<Student>) {
    if (!this::students.isInitialized) {
        this.students = mutableListOf()
    }
    students.forEach {
        this.students.add(it)
    }
}
```

```kotlin
      for(Iterator var4 = $this$forEach$iv.iterator(); var4.hasNext(); var10000.add(it)) {
         Object element$iv = var4.next();
         it = (Student)element$iv;
         int var7 = false;
         var10000 = this.students;
         if (var10000 == null) { // 포문마다 null check 진행
            Intrinsics.throwUninitializedPropertyAccessException("students");
         }
      }
```

# Lazy properties

[Lazy properties](https://kotlinlang.org/docs/delegated-properties.html#lazy-properties) : `lazy()`는 람다를 가져와서 `lazy`의 인스턴스를 반환하는 함수로, `lazy properties`를 구현하기 위한 위임 역할을 수행한다. 
해당 프로퍼티에 대한 첫 번째 `get()`호출은 `lazy()`에 전달된 람다식을 실행하고 결과를 기억한다. 이후 호출된 `get()`은 단순히 기억된 결과를 반환한다.

```kotlin
val lazyValue: String by lazy {
    println("computed!")
    "Hello"
}

fun main() {
    println(lazyValue)
    println(lazyValue)
}

// 출력 결과
computed!
Hello
Hello
```

lateinit은 필요할 경우 언제든 초기화가 가능한 속성이지만, `lazy`는 생성 후 값을 변경할 수 없는 `val(immutable)`로 선언된다.
```kotlin
var number: Int by lazy { // Error! : Change to val
	5
}
```

* 호출 시점에 by lazy 정의에 의해서 초기화를 진행한다.
* val(immutable)에서만 사용이 가능하다.
* val이므로 값을 교체하는 건 불가능하다.
* lazy을 사용하는 경우 기본 Synchronized로 동작한다.

기본적으로 `lazy properteis`는 하나의 쓰레드에 의해 계산되기 때문에 동기화가 보장 되며 모든 스레드에서 동일한 값을 전달 받는다.  


## `lazy` 내부소스 톺아보기

```kotlin
public actual fun <T> lazy(initializer: () -> T): Lazy<T> = SynchronizedLazyImpl(initializer)
```
lazy 내부에서는 초기화를 진행할 람다식을 가지고 `SynchronizedLazyImpl`을 구현하고 있다.

`SynchronizedLazyImpl`의 내부 소스는 다음과 같다.

```java
private class SynchronizedLazyImpl<out T>(initializer: () -> T, lock: Any? = null) : Lazy<T>, Serializable {
    private var initializer: (() -> T)? = initializer
    @Volatile private var _value: Any? = UNINITIALIZED_VALUE
    private val lock = lock ?: this

    override val value: T
        get() {
            val _v1 = _value
            if (_v1 !== UNINITIALIZED_VALUE) {
                @Suppress("UNCHECKED_CAST")
                return _v1 as T
            }

            return synchronized(lock) {
                val _v2 = _value
                if (_v2 !== UNINITIALIZED_VALUE) {
                    @Suppress("UNCHECKED_CAST") (_v2 as T)
                } else {
                    val typedValue = initializer!!()
                    _value = typedValue
                    initializer = null
                    typedValue
                }
            }
        }

    override fun isInitialized(): Boolean = _value !== UNINITIALIZED_VALUE

    override fun toString(): String = if (isInitialized()) value.toString() else "Lazy value not initialized yet."

    private fun writeReplace(): Any = InitializedLazyImpl(value)
}
```

`value`의 `getter`에서 값이 초기화되었는지 확인하고, 그렇지 않다면 쓰레드를 `lock`하고 initializer를 실행 및 값을 저장하는 것을 알 수 있다.




참고자료 :

https://thdev.tech/kotlin/2018/03/25/Kotlin-lateinit-lazy/

https://kotlinlang.org/docs/delegated-properties.html#providing-a-delegate

https://kotlinlang.org/docs/properties.html#backing-fields
