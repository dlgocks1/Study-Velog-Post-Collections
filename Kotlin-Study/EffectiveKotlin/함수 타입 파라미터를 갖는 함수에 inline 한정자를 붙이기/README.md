코틀린 표준 라이브러리의 고차 함수를 살펴보면 대부분 inline 한정자가 붙어 있는 것을 확인할 수 있다.

`repeat`함수를 보자.

```
inline fun repeat(times: Int, action: (Int) -> Unit) {
	for (index in 0 until times) {
    	action(index)
    }
}
```

inline 한정자의 역할은 `함수를 호출하는 부분`을 `함수의 본문`으로 대체하는 것이다. 예를 들어 `repreat`함수를 호출하는 코드가 있다면

```
repeat(10) {
	print(it)
]
```

컴파일 시점에 해당 소스 부분이 다음과 같이 대체된다.

```
for (index in 0 until 10) {
	print(index)
}
```

이처럼 `inline`한정자를 붙여 함수를 만들면, 굉장히 큰 변화가 일어납니다. 일반적인 함수를 호출하면 함수 본문으로 점프하는 `branch`가 수행되는데 이처럼 함수의 본문으로 대체하면, 이러한 점프가 일어나지 않는다.

그외에도 다음과 같은 장점이 있다.

1. 타입 아규먼트에 `refied`한정자를 붙여서 사용할 수 있다.
   (이에 관해선 이 후 설명)

2. 함수 타입 파라미터를 가진 함수가 훨씬 빠르게 동작합니다.

3. `비지역(non-local)` 리턴을 사용할 수 있다.

### 타입 아규먼트를 `reified`로 사용할 수 있다.

구버전의 자바에는 제네릭이 없었다. 2004년 이후부터 제네릭을 사용할 수 있다. 하지만 JVM 바이트코드에는 제네릭이 존재하지 않는다.
따라서 컴파일을 하면, 제네릭 타입과 관련된 내용이 제거된다.**(런타임 시에 해당 타입이 무슨 타입인지 알 수 없음!)** 예를 들어 `List<Int>`를 컴파일하면 `List`로 바뀐다. 그래서 객체가 `List`인지 확인하는 코드는 사용할 수 있지만, `List<Int>`인지 확인하는 코드는 사용할 수 없다.

```
any is List<Int> // 오류
any is List<*> // OK
```

같은 이유로 다음과 같은 타입 파라미터에 대한 연산도 오류가 발생한다.

```
fun <T> printTypeName() {
	print(T::class.simpleName) // 오류
}
```

> 함수를 인라인으로 만들면, 이러한 제한을 무시할 수 있다. 함수 호출이 본문으로 대체되므로, `reified`한정자를 지정하면, 타입 파라미터를 사용한 부분이 타입 아규먼트로 대체된다.

![](https://velog.velcdn.com/images/cksgodl/post/907641cd-d704-4a7f-8a3d-55739b4fde82/image.png)

```
// reified 추가
inline fun <reified T> printTypeName() {
    println(T::class.simpleName)
}

printTypeName<Int>() // Int
printTypeName<Char>() // Char
printTypeName<String>() // String
```

컴파일 하는 동안 `printTypeName`의 본문이 실제로 대체된다. 따라서 실제론 다음과 같이 컴파일된다.

```
print(Int::class.simpleName)
print(Char::class.simpleName)
print(String::class.simpleName)
```

만약 해당 함수를 `reified`한정자를 사용하지 않고 동일한 구현을 하고자 한다면 다음과 같이 함수의 타입을 넘겨 주어야 한다.

```
inline fun <T> printTypeName(classType: Class<T>) {
    println(classType)
}

printTypeName(Int::class.java) // int
printTypeName(String::class.java) // class java.lang.String
printTypeName(Char::class.java) // char
```

또한 다음과 같은 `Warning`이 발생한다.

> Expected performance impact from inlining is insignificant. Inlining works best for functions with parameters of functional types
> 인라인으로 얻을 수 있는 성능의 영향이 미비하다. 함수 파라미터가 존재 할 때 인라인 함수를 사용해라.

---

`reified`는 굉장히 유용한 한정자이다. 예를 들어 표준 라이브러리 `filterInstance`도 특정 타입의 요소를 필터링할 때 사용된다.

```
class Worker
class Manager

val employees: List<Any> =
    listOf(Worker(), Manager(), Worker())

val workers: List<Worker> = employees.filterIsInstance<Worker>()
```

- `filterInstance`내부 구현

```
public inline fun <reified R, C : MutableCollection<in R>> Iterable<*>.filterIsInstanceTo(destination: C): C {
    for (element in this) if (element is R) destination.add(element)
    return destination
}
```

### 함수 타입 파라미터를 가진 함수가 훨씬 빠르게 동작한다.

실제로 `inline`한정자를 쓰는 함수내 함수 파라미터가 없으면 다음과 같은 경고를 뛰운다.

> 인라인으로 얻을 수 있는 성능의 영향이 미비하다. 함수 파라미터가 존재 할 때 인라인 함수를 사용해라.

모든 함수가 `inline`한정자를 붙일 때 좀 더 빠르게 동작한다. 함수 호출과 리턴을 위해 점프하는 과정과 백스택을 추적하는 과정이 사라지기 때문이다.

컴퓨터 구조때 배운 것처럼 함수를 실행하면 기존 내용을 레지스터에 저장하고 새로운 코드로 점프하는 과정이 수행되지 않는다. (함수 호출 과정)

![](https://velog.velcdn.com/images/cksgodl/post/201b4466-c3d9-48ab-862c-5ef5da524c91/image.png)

그래서 표준 라이브러리에 있는 간단한 함수들에는 대부분 `inline`한정자가 붙어 있다.

하지만 함수 파라미터를 가지지 않는 함수에서는 이러한 차이가 큰 성능 차이를 발생시키지 않는다. 그 이유는 함수를 객체로서 조작할 때 발생하는 문제를 이해해야 한다. 함수 리터럴을 사용해 만들어진 이러한 종류의 객체는 어떤 방식이로든 저장되고 유지되어야 한다. 코틀린/JVM에서는 JVM 익명 클래스 또는 일반 클래스를 기반으로, 함수를 객체로 만들어 낸다.

예를 들어 다음과 같은 람다표현식

```
val lambda: () -> Unit {
	// ...
}
```

은 클래스로 컴파일 된다.

```
Function0<Unit> lambda = new Function0<Unit>() {
	pulibc Unit invoke() {
    	// code
    }
}
```

인텔리제이에서는 Tools -> Kotlin -> Show Kotlin Bytecode를 선택하면 해당 소스의 바이트코드까지 볼 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/b200f4fa-d283-4a45-820e-9ec1b541c9a1/image.png)

- Kotlin 코드

```
class ReifiedTest() {
    val decompliedLambda: () -> Unit = {
        // 코드
    }

    fun main() {
        decompliedLambda()
    }
}
```

- Decompiled 자바 코드

```
public final class ReifiedTest {
   @NotNull
   private final Function0 decompliedLambda;

   @NotNull
   public final Function0 getDecompliedLambda() {
      return this.decompliedLambda;
   }

   public final void main() {
      this.decompliedLambda.invoke();
   }

   public ReifiedTest() {
      this.decompliedLambda = (Function0)null.INSTANCE;
   }
}
```

- invoke 바이트 코드

```
  public final invoke()V
   L0
    LINENUMBER 23 L0
    RETURN
   L1
    LOCALVARIABLE this LReifiedTestKt$decompliedLambda$1; L0 L1 0
    MAXSTACK = 0
    MAXLOCALS = 1
```

JVM에서 아규먼트가 없는 함수 타입은 `Function0`타입으로 변환된다.

- `() -> Unit` 은 `Function0<Unit>`으로 컴파일
- `() -> Int` 은 `Function0<Int>`으로 컴파일
- `(Int) -> Int` 은 `Function1<Int, Int>`으로 컴파일
- `(Int,Int) -> Int` 은 `Function2<Int, Int, Int>`으로 컴파일

이러한 모든 인터페이스는 모두 코틀린 컴파일러에 의해 생성된다. 이들은 요청이 있을 때 생성되므로, 이를 명시적으로 사용할 수는 없다. 대신 함수 타입을 사용할 수 있다. 함수 타입이 단순한 인터페이스라는 것을 알면 추가적인 가능성이 보이게 된다.

```
class OnClickListener : () -> Unit { // 함수 타입 또한 단순한 인터페이스다!
    override fun invoke() {
        // TODO
    }
}
```

**함수 본문을 객체로 랩하면 코드의 속도가 느려진다.**그래서 다음과 같은 두 함수가 있을 때, 첫 번째 함수가 더 빠른 것이다.

```
inline fun repeat(times: Int, action: (Int) -> Unit) {
    for (index in 0 until times) {
        action(index)
    }
}
```

```
fun nonInlineRepeat(times: Int, action: (Int) -> Unit) {
    for (index in 0 until times) {
        action(index)
    }
}
```

위의 두 가지 함수를 직접 자바로 디컴파일했을 때 어떠한 일이 일어날까?

```
fun main() {

    repeat(5) {
        println(it)
    }

    nonInlineRepeat(5) {
        println(it)
    }

}
```

자바로 디컴파일한 결과이다.

```
   public static final void main() {
      int times$iv = 5;
      int $i$f$repeat = false;
      int index$iv = 0;

      for(byte var3 = times$iv; index$iv < var3; ++index$iv) {
         int var5 = false;
         System.out.println(index$iv);
      }

      nonInlineRepeat(5, (Function1)null.INSTANCE);
   }
```

`nonInlineRepeat` 이라는 함수 자체를 객체로 랩(wrap)하여 메인에서 전달하고 있다.(객체를 생성하고 있음) 이는 [효율성 - 불필요한 객체 생성을 피하라](https://velog.io/@cksgodl/Kotlin-%ED%9A%A8%EC%9C%A8%EC%84%B1-%EB%B6%88%ED%95%84%EC%9A%94%ED%95%9C-%EA%B0%9D%EC%B2%B4-%EC%83%9D%EC%84%B1%EC%9D%84-%ED%94%BC%ED%95%98%EB%9D%BC)에서 설명했던 것처럼 필요없는 객체를 생성하기에 코드의 속도가 느려진다.

`inline repeat`함수는 본문의 내용을 메인함수 내에서 그대로 실행하기에 속도의 저하가 없다.

> Effecttive 코틀린의 저자에서 1억번의 반복을 하는 특정 코드를 실행했을 때, 약 10%의 차이가 발생한다고 한다. 이러한 처리를 할 때마다 10%의 시간이 계속 누적될 것!

`인라인 함수`와 `인라인 함수가 아닌 함수`의 더 중요한 차이는 함수 리터널 내부에서 지역 변수를 캡처할 때 볼 수 있다. 캡처된 값은 객체로 래핑되어야 하며, 사용할 때마다 객체를 통해 작업이 이루어져야 한다. 예를들어

```
var l = 1L

nonInlineRepeat(20) {
    l += it
}
```

인라인이 아닌 람다 표현식에서는 지역 변수 `l`을 직접 사용할 수 없다. `l`은 컴파일 과정 중 다음과 같이 레퍼런스 객체로 래핑되고, 람다 표현식 내부에서 이를 사용한다.

다음 예를 보자.

```
fun main() {

    var l = 1L
    val repeatTimes = 20
    repeat(repeatTimes) {
        l += it
    }

    nonInlineRepeat(repeatTimes) {
        l += it
    }

}
```

`l`이라는 변수를 인라인 함수, 인라인이 아닌 함수에서 각각 실행했을 때 결과이다.

```
   public static final void main() {
      final LongRef l = new LongRef();
      l.element = 1L;
      int repeatTimes = 20;
      int $i$f$repeat = false;
      int index$iv = 0;

      for(byte var4 = repeatTimes; index$iv < var4; ++index$iv) {
         int var6 = false;
         l.element += (long)index$iv;
      }

      nonInlineRepeat(repeatTimes, (Function1)(new Function1() {
         // $FF: synthetic method
         // $FF: bridge method
         public Object invoke(Object var1) {
            this.invoke(((Number)var1).intValue());
            return Unit.INSTANCE;
         }

         public final void invoke(int it) {
            LongRef var10000 = l;
            var10000.element += (long)it;
         }
      }));
```

인라인 함수(`repeat`)에서는 `l`이라는 레퍼런스를 가지고 계속 반복된 작업을 수행하여 새로운 레퍼런스를 생성하지 않는다.
하지만 논인라인 함수(`nonInlineRepeat`)에서는 `LongRef var10000 = l;`실행될 때 마다 지역 변수가 래핑되어 `LongRef`참조 타입을 계속 생성하는 것을 볼 수 있다. 위에서 설명한 것과 같이 불필요한 객체(참조 타입)을 생성하지 않음으로 속도가 빨라진다. **이는 속도면에서 큰 차이를 낸다.**

일반적으로는 함수 타입 파라미터를 활용해서 유틸리티 함수를 만들 때(컬렉션 처리)는 그냥 인라인 파라미터를 붙여 준다 생각하는 것이 좋다. 표준 라이브러리의 대부분은 인라인 한정자로 구현된다.

### 비지역적 리턴(non-local return)을 사용할 수 있다.

이전에 살펴보았던 `nonInlineRepeat`은 제어문처럼 코드를 작성하였다. 일반적인 if 조건문, for 반복문과 비교해서 살펴보자.

```
fun main() {

    if (value != null) {
        print(value)
    }

    for (i in 1..10) {
        print(i)
    }

    nonInlineRepeat(10) {
        println(it)
    }

}
```

셋다 모두 제어문 처럼 실행되지만 중요한 차이점이 있는데, 바로 `nonInlineRepeat`에서는 내부에서 리턴을 사용할 수 없다는 것이다.

```
    nonInlineRepeat(10) {
        println(it)
        return // 'return' is not allowed here
    }
```

이는 함수 리터널이 컴파일될 때, 함수가 객체로 래핑되어서 발생하는 문제이다. 함수 자체가 다른 클래스에 위치하므로, `return`을 사용하여 `main`으로 돌아올 수 없는 것이다. 하지만 인라인 함수라면 이런 문제가 없다. 함수가 `main`내부에 박히기 때문이다.

```
repeat(10) {
    println(it)
    return // Possible!
}
```

### inline 한정자의 비용

`inline` 한정자는 굉장히 유용한 한정자지만, 모든 곳에 사용할 수는 없다. 대표적인 예로 인라인 함수는 재귀적으로 동작할 수 없다. 이를 재귀적으로 사용하게되면, 무한하게 대체되는 문제가 발생하게 된다. 이러한 문제는 인텔리제이가 오류로 잡아주지 못하므로 굉장히 위험하다.

```
// 사이클이 존재해도 런타임전까지 오류발생 x
inline fun a() { b() }
inline fun b() { c() }
inline fun c() { a() }
```

또한 인라인 함수는 더 많은 가시성 제한을 가진 요소를 사용할 수 없다. `public` 인라인 함수 내부에서는 `private`과 `internal` 가시성을 가진 함수와 프로퍼티를 사용할 수 없다.

같은 파일, 모듈내에 선언하여도 에러가 발생

```
private class Student() {}

inline fun a() {
    val student = Student() // 공용-API 인라인 함수는 공용-API가 아닌 공용 생성자 Student()에 액세스할 수 없습니다.
    b()
}
```

inline 한정자가 `private`이면 접근이 가능하다.

```
private class Student() {}

private inline fun a() {
    val student = Student()
}
```

이처럼 인라인 함수는 구현을 숨길 수 없으므로, 클래스에 거의 사용되지 않는다.

추가적인 예로 인라인함수의 중첩을 생각해보자. 다음과 같이 3을 출력하는 함수를 구현하자.

```
inline fun threePrint() {
    print(3)
}
```

3을 더 출력하고 싶어서 인라인 함수를 중첩해보자.

```
inline fun threeThreePrint() {
    threePrint()
    threePrint()
    threePrint()
}

inline fun threeThreeThreePrint() {
    threeThreePrint()
    threeThreePrint()
    threeThreePrint()
}
```

    threeThreeThreePrint() // 333333333

그럼 다음과 같은 함수는 어떻게 디컴파일 될까?

```
public static final void threeThreeThreePrint() {
      byte var3 = 3;
      System.out.print(var3);
      var3 = 3;
      System.out.print(var3);
      // 8번 반복...
      var3 = 3;
      System.out.print(var3);
   }
```

너무나 쉽게 코드의 크기가 커진다. 서로 중첩으로 호출하는 인라인 함수가 많아지면, 코드가 기하급수적으로 증가함으로 위험하다.

### crossinline과 noinline

함수를 인라인으로 만들고 싶지만, 어떤 이유로 일부 함수 타입 파라미터는 `inline`으로 받고 싶지 않은 경우가 있을 수 있다. 이러한 경우에는 다음과 같은 한정자를 사용한다.

- crossline : 아규먼트로 인라인 함수를 받지만, 비지역적 리턴을 함수는 받을 수 없게 만든다. 인라인으로 만들지 않은 다른 람다 표현식과 조합해서 사용할 때 문제가 발생하는 경우 활용한다.

- noinline : 아규먼트로 인라인 함수를 받을 수 없게 만든다. 인라인 함수가 아닌 함수를 아규먼트로 사용하고 싶을 때 활용한다.

```
inline fun requestNewToken(
    hasToken: Boolean,
    crossinline onRefresh: () -> Unit,
    noinline onGenerate: () -> Unit
) {
    if (hasToken) {
        httpCall("get-token", onGenerate)
        // 인라인이 아닌 함수를 아규먼트로 함수에 전달하려면
        // noinline을 사용한다
    } else {
        httpCall("refresh-token") {
            onRefresh()
            // Non-local 리턴이 허용되지 않는 컨텍스트에서
            // inline 함수를 사용하고 싶다면 crossinline을 사용한다.
            onGenerate()
        }
    }
}

fun httpCall(url: String, callback: () -> Unit) {
    // ..
}
```

두 한정자의 의미를 확실하게 기억하면 좋겠지만, `IDEA`가 필요할 때 알아서 제안을 해 주므로 대충 알아둬도 된다.

![](https://velog.velcdn.com/images/cksgodl/post/61f47303-6cad-4316-bc00-cc14fb6ae3c1/image.png)

실제로 동작하는 모습을 디컴파일 해보자.

```
fun main() {
    requestNewToken(false,
        onGenerate = {
            println("onGenerate : False")
        },
        onRefresh = {
            println("onRefresh : False")
        }
    )
}
```

```
   public static final void main() {
      Function0 onGenerate$iv = (Function0)null.INSTANCE;
      // ..
      httpCall("refresh-token", (Function0)(new onGenerate$iv));
   }
```

### 정리

> 인라인 함수는 `함수 본문의 내용`을 함수를 호출하는 부분으로 꺼내는 것이다.

이러한 방식으로 코드를 작성하면 `함수 호출`이 발생하지 않아 비용이 없고, 빠르며 다음과 같은 특징이 있다.

- `reified`한정자를 지정하여 함수의 타입을 넘길 수있다.
- 함수 타입 파라미터를 가진 함수타입이 훨씬 빠르게 작동한다. (함수를 객체로 래핑하지 않아도 됨)

```
    repeat(5) {
        println(it)
    }

    nonInlineRepeat(5) {
        println(it)
    }
```

```
  public static final void main() {
      int times$iv = 5;
      int $i$f$repeat = false;
      int index$iv = 0;

      for(byte var3 = times$iv; index$iv < var3; ++index$iv) {
         int var5 = false;
         System.out.println(index$iv);
      }

      nonInlineRepeat(5, (Function1)null.INSTANCE);
   }
```

- 지역 변수를 캡처할 때 레퍼런스를 생성하기 때문에 속도가 느리다.
- 비지역적 리턴을 사용할 수 있다.(함수 본문으로 대체되기 때문)
- 인라인 함수가 중첩되면 본문이 기하급수적으로 증가할 수 있다.

---

- crossline : Non-local 리턴이 허용되지 않는 컨텍스트에서 `inline` 함수를 사용하고 싶다면 `crossinline`을 사용한다.

- noinline : 인라인이 아닌 함수를 아규먼트로 함수에 전달

---

인라인 함수가 사용되는 주요 사례는 다음과 같다.

- print 함수처럼 매우 많이 사용되는 경우
- `filterIsInstance`함수처럼 타입 아규먼트로 `refied`타입을 전달받는 경우
- 함수 타입 파라미터를 갖는 톱레벨 함수를 정의해야 하는 경우, 특히 컬렉션 처리 함수와 같은 헬퍼 함수`(map, flatMap, joinToString 등)`, 스코프 함수`(alos, apply, let 등)`, 톱레벨 유틸리티 함수`(repeat, run, with)`의 경우 등
