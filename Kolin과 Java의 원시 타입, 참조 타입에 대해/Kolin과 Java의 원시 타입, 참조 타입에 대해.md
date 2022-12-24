# 자바의 원시 타입과 참조 타입에 대해

자바의 데이터타입에는 크게 두 가지가 있다.
1. `원시 타입(Privimitive Type)` - Effective Kotlin 책에서는 `기본 자료형`이라 표기하고 있다.
2. `참조 타입(Reference Type)`  Effective Kotlin 책에서는 `랩(wrap)한 자료형`이라 표기하고 있다.

원시 타입은 정수, 실수, 문자, 논리 리터럴등의 실제 데이터 값을 저장하는 타입이다.
원시 타입의 예) `boolean`, `char`, `byte`, `short`, `int`, `long`, `float`, `double` 과 같은 실제 데이터

참조 타입은 객체(Object)의 번지를 참조(주소를 저장)하는 타입으로 메모리 번지 값을 통해 객체를 참조하는 타입이다.
참조 타입의 예)`문자열`, `배열`, `Enum`, `클래스`, `interface`등이 있다.  

## 원시 타입과 참조 타입의 차이

1. nullable 여부
원시 타입은 null을 담을 수 없지만, 참조 타입은 가능하다.
```
int i = null; // Error!
Integer integer = null; // Good!
```

2. 제너릭 사용 가능 여부
원시타입은 제너릭 타입에서 사용할 수 없지만, 참조 타입은 가능하다.
```
List<Int> list; // 불가능
List<Integer> list; // 가능
```

3. 접근 속도
원시 타입은 `스택 메모리`에 저장되며 접근할 때 한번의 참조면 충분하다.
하지만 참조 타입은 하나의 인스턴스이기 때문에 `스택메모리`에는 참조 값만 존재하고, 실제 값은 `힙 메모리`에 존재한다. 값을 필요로 할때 언박싱 과정을 거쳐야하니 접근속도가 느리다.

---

# 코틀린에서의 원시 타입과 참조 타입?

> 코틀린은 원시 타입과 참조타입을 따로 구분하지 않는다.

즉 자버처럼 `int`와 `Integer`로 구별하지 않으며 `int`하나만 존재한다.

![](https://velog.velcdn.com/images/cksgodl/post/87afa631-2aee-49b3-be98-dc77be3b6a70/image.png)

그렇다면 `문자열`, `배열`, `클래스`와 같은 참조 타입을 어떻게 표현할까? 이는 코틀린/JVM에서 컴파일 시 자동으로 원시 타입과 참조 타입을 결정해서 만들어 준다.

### nullable

위에서 설명했듯이 코틀린에서의 `nullable`한 타입 (`Int?`, `Boolean?` 등)은 자바의 원시타입으로 표현할 수 없기에 `wrapper type` 즉 참조 타입으로 컴파일 된다.
```
val nullabelInt: Int? = null

Integer nullabelInt = (Integer)null;
```

### generic
또한 제너릭의 경우도 참조 타입으로 컴파일된다. `null`값 이나 `nullable`타입을 사용하지 않았음에도 Integer리스트로 만들어지는 것을 볼 수 있다.
```
val listOfInts = listOf(1, 2, 3)

List listOfInts = CollectionsKt.listOf(new Integer[]{1, 2, 3});
```
### Any, Any?

자바에서는 `Object`가 최상위 계층이며 코틀린에서는`Any`가 모든 타입의 최상위 계층이다.
즉 `Any`타입은 컴파일 시 `Object`로 변환된다.

그렇다면 `Any`, `Any?`는 각각 무슨 타입으로 변환될까?
```
val anyType: Any = "any"
val nullableAny: Any? = "any?"
```

`Object`는 참조 타입으로 `nullable`함으로 다음 결과는 동일한 `Object`를 반환한다.

```
 private static final Object anyType = "any";
 private static final Object nullableAny = "any?";

public static final Object getAnyType() {
	return anyType;
}

public static final Object getNullableAny() {
	return nullableAny;
}
```

### Nothing, Nothing?, Unit, Unit? 

`Nothing`은 어떤 값도 포함하지 않는 타입이며, 모든 타입의 서브 클래스이다. `private constructor`로 정의되어 있어 인스턴스를 생성할 수 없다.
```
/**
 * Nothing은 인스턴트 생성이 불가능하다. 이는 값이 존재하지 않는다는 것을 나타내기 위해 사용된다.
 * 예를 들어 함수가 Nothing을 반환한다면 그 함수는 언제나 exception을 throws해야 한다.
 */
public class Nothing private constructor()
```

위의 설명과 같이 언제나 `excepiton`을 반환하는 함수, 종료되지 않는 함수(무한 루프를 빠져나오지 못하는 함수)는 Nothing을 반환해야 한다.

언제나 예외를 반환하는 함수를 코틀린/JVM에서는 어떻게 디컴파일할까?
```
fun nothingFunc(): Nothing {
    throw Exception("Nothing") // Nothing을 반환하는 함수에서는 어떠한 것도 return할 수 없다.
}
```

이는 Void 및 Throwable로 디컴파일 되는 것을 확인할 수 있다.

```
   public static final Void nothingFunc() {
      throw (Throwable)(new Exception("Nothing"));
   }
```

그렇다면 `Nothing?`은 어떨까? 이러한 함수는
1. 종료되지 않는 함수
2. 예외를 던지는 함수
3. null을 리턴하는 함수
로 경우의 수가 나뉠 수 있다.


```
fun nothingFunc(): Nothing? {
    return null
}
```

`null`을 반환하는 다음과 같은 함수를 디컴파일해보자

```
public static final Void nothingFunc() {
	return null;
}
```
이는 Void함수 내에서 null을 반환하는 함수로 디컴파일 되는 것을 확인할 수 있다.

이는 클린코드에서 말하는 NULL을 반환하거나 인수로 전달하지 마라에 위반하는 것을 알 수 있다. 이에 따라 코틀린에서도 `Nothing?`과 같은 명확하지 않은 반환타입을 쓰는 것은 옳지 않다.

그렇다면 `Unit`은 `Void`로 디컴파일 되며 `Unit?`은 어떠한 타입을 반환할까?

```
fun unitFunc(): Unit? {
    return null
}
```

```
public static final Unit unitFunc() {
	return null;
}
```

자바에서도 `Unit`이라는 Object를 사용하여 null을 반환해주고 있다. 해당 `Unit` 오브젝트는 코틀린/JVM에 존재하는 오브젝트로 `void`는 null을 반환할 수 없으니 `void`와 동일한 타입을 가지지만, null을 리턴할 수 있는 `Unit`을 사용해 null을 반환한다.
```
/**
 * The type with only one value: the `Unit` object. This type corresponds to the `void` type in Java.
 */
public object Unit {
    override fun toString() = "kotlin.Unit"
}
```

---

# 코틀린에서는 효율성을 위해 원시타입(기본 자료형)을 사용하라

[효율성 - 불필요한 객체 생성을 피하라](https://velog.io/@cksgodl/Kotlin-%ED%9A%A8%EC%9C%A8%EC%84%B1-%EB%B6%88%ED%95%84%EC%9A%94%ED%95%9C-%EA%B0%9D%EC%B2%B4-%EC%83%9D%EC%84%B1%EC%9D%84-%ED%94%BC%ED%95%98%EB%9D%BC)에서 공부했던 내용 중 하나이다.

JVM은 숫자와 문자 등의 기본적인 요소를 나타내기 위한 특별한 기본 내장 자료형을 가지고 있다. 이를 `기본 자료형(primitives)`라고 한다. 코틀린/JVM 컴파일러는 내부적으로 최대한 이러한 기본 자료형을 사용한다. 다만 다음과 같은 두 가지 상황에는 기본 자료형을 랩(wrap)한 자료형(참조 타입)이 사용된다.

1. nullable한 타입을 연산할 때
2. 타입을 제네릭으로 사용할 때

```
Kotlin.Int == java.int
Kotlin.Int? == Java.Integer
Kotlin.List<Int> == Java<Integer>
```

**참조 타입 대신 원시 타입을 사용하게 코드를 최적화 해야 한다.** 하지만 이런 코드의 최적화는 숫자에 대한 작업이 여러 번 반복되어야(큰 컬렉션을 처리할 때) 의미가 있다.


# 참고 자료:

https://velog.io/@gillog/%EC%9B%90%EC%8B%9C%ED%83%80%EC%9E%85-%EC%B0%B8%EC%A1%B0%ED%83%80%EC%9E%85Primitive-Type-Reference-Type

https://0391kjy.tistory.com/57
