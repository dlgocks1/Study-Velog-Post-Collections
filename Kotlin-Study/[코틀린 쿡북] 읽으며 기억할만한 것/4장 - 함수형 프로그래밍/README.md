# 4장 함수형 프로그래밍

[리스트 값 합치기](#리스트-값-합치기)
[꼬리 재귀 - tail recursion](#꼬리-재귀)

## 리스트 값 합치기

### fold 사용하기

`fold`함수를 활용하면 시퀀스나 컬렉션을 하나의 값으로 축약(`reduce`)할 수 있습니다.

`fold`의 내부 구현체는 다음과 같습니다.

```java
public inline fun <T, R> Iterable<T>.fold(initial: R, operation: (acc: R, T) -> R): R {
    var accumulator = initial
    for (element in this) accumulator = operation(accumulator, element)
    return accumulator
}
```

활용 예는 다음과 같습니다.

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)
// initial -> 초기 값
// operation -> 동작할 람다 식 (acc 기존 값, n 현재 값)
println(numbers.fold(0) { acc, n -> acc + n }) // 15
```

각각의 연산의 결과값이 `acc`에 들어갑니다.

```kotlin
numbers.fold(0) { acc, n ->
	println("acc = $acc, n = $n")
	acc + n
}
// 출력 값
acc = 0, n = 1 // 초기 initial value = 0
acc = 1, n = 2
acc = 3, n = 3
acc = 6, n = 4
acc = 10, n = 5
```

또한 책의 예제에서는 피보나치 수를 `fold`를 활용하여 구현하는 재미있는 예제가 있습니다.

```kotlin

fun fibonacciFold(n: Int) =
    (2 until n).fold(1 to 1) { (prev, curr), _ ->
        println("prev $prev, curr $curr")
        curr to (prev + curr)
    }.second

println(fibonacciFold(10)) // 55

// 출력
prev 1, curr 1
prev 1, curr 2
prev 2, curr 3
prev 3, curr 5
prev 5, curr 8
prev 8, curr 13
prev 13, curr 21
prev 21, curr 34
```

누적 값의 타입이 `Pair`, 즉 숫자 타입이 아니여도 `fold`를 활용할 수 있음을 강조하고 있습니다.

### reduce 사용하기

비어 있지 않는 컬렉션의 값을 축약하고 싶지만, 초기값을 설정하고 싶지 않을 때 활용할 수 있는 것이 `reduce`입니다.

`reduce`의 내부 구현은 다음과 같습니다.

```java
public inline fun <S, T : S> Iterable<T>.reduce(operation: (acc: S, T) -> S): S {
	// 이터레이터를 설정합니다.
    val iterator = this.iterator()

    // 비어있는 컬렉션이면 에러가 발생합니다.
    if (!iterator.hasNext()) throw UnsupportedOperationException("Empty collection can't be reduced.")

    // 초기값을 가져옵니다.(첫 번째 원소)
    var accumulator: S = iterator.next()

    // 연산을 진행하며 acc를 업데이트 합니다.
    while (iterator.hasNext()) {
        accumulator = operation(accumulator, iterator.next())
    }
    return accumulator
}
```

내부 구현체에서도 볼 수 있듯이, 비어 있는 컬렉션은 예외가 발생하게 됩니다.

이러한 `reduce`를 활용할 때 주의점이 하나 있습니다.

- 첫 번째는 비어있을 수 있는 컬렉션에 적용하지 말 것

- 두 번째는 누적자를 초기화하고 컬렉션의 다른 값에 추가 연산을 필요로 하지 않을 경우에만 사용할 것

두 번째의 예는 다음과 같습니다.

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)
println(numbers.reduce { acc, i ->
    println("acc $acc, i $i")
    acc + i * 2
})

// 출력 값
acc 1, i 2
acc 5, i 3
acc 11, i 4
acc 19, i 5
29
```

30이 출력됬어야 하지만 초기 값 1을 acc에 바로 대입함으로써`i *2` 연산이 적용되지 않은 모습입니다.

---

## 꼬리 재귀

꼬리 재귀를 활용해 재귀적인 연산의 스택메모리를 절약할 수 있습니다.

다음은 팩토리얼을 재귀를 활용해 구현한 예제입니다.

```kotlin
fun recursiveFatorial(n: Long): BigInteger =
    when (n) {
        0L, 1L -> BigInteger.ONE
        else -> BigInteger.valueOf(n) * recursiveFatorial(n - 1)
    }
```

간단하게 구현할 수 있지만,

```kotlin
println(recursiveFatorial(10_000)) // StackOverflowError!!
```

`10_000` 기본적으로 재귀 프로세스가 JDK1.8기준으로 `1Kb`가 넘게되면 스택오버플로우가 발생하게 됩니다.

하지만 꼬리재귀를 활용하게 되면 이런 스택메모리를 절약할 수 있습니다.

```kotlin
// JvmOverloads를 활용하여 Default Argument를 JVM상에서 지원하게 하기
@JvmOverloads
tailrec fun factorial(
    n: Long,
    acc: BigInteger = BigInteger.ONE
): BigInteger =
    when (n) {
        0L -> BigInteger.ONE
        1L -> acc
        // 꼬리 재귀 함수는 본인 함수만을 리턴해야 함 -> factorial(/.../)
        else -> factorial(n - 1, acc * BigInteger.valueOf(n))
    }
```

`tailrec` 한정자를 붙임으로써 컴파일러에게 해당 재귀 호출을 최적화해야 한다고 알릴 수 있습니다.

그렇다면 컴파일러는 이를 어떻게 해석할까요?

`tailrec`이 붙지 않은 재귀는 다음과 같습니다.

```java
   // 재귀를 활용한 factorial 자바 소스
   @NotNull
   public static final BigInteger recursiveFatorial(long n) {
      BigInteger var10000;
      if (n != 0L && n != 1L) {
         var10000 = BigInteger.valueOf(n);
         BigInteger var4 = var10000;
         // 재귀를 수행합니다.
         BigInteger var5 = recursiveFatorial(n - 1L);
         var10000 = var4.multiply(var5);
      } else {
         var10000 = BigInteger.ONE;
      }

      return var10000;
   }
```

코틀린 코드와 같이 재귀를 타고 들어감으로써 스택이 쌓이는 것을 알 수 있습니다.

하지만 `tailrec`을 활용해 컴파일러가 효율적으로 최적화한 코드는 다음과 같습니다.

```kotlin
   @JvmOverloads
   @NotNull
   public static final BigInteger factorial(long n, @NotNull BigInteger acc) {
   	  // while문을 통해 더이상 재귀를 진행하지 않습니다.
      while(true) {
         BigInteger var10000;
         if (n == 0L) {
            var10000 = BigInteger.ONE;
         } else {
            if (n != 1L) {
               long var7 = n - 1L;
               BigInteger var10001 = BigInteger.valueOf(n);
               BigInteger var6 = var10001;
               var10001 = acc.multiply(var6);
               acc = var10001;
               n = var7;
               continue;
            }

            var10000 = acc;
         }

         return var10000;
      }
   }
```

`while`를 활용하는 반복 알고리즘으로 리팩토링된 것을 확인할 수 있습니다. 이처럼 `tailrec`을 활용하기 위한 함수의 조건은 다음과 같습니다.

- 함수는 반드시 수행하는 마지막 연산으로서 자기 자신을 호출해야 합니다.
- try/catch/finally 블록 안에서는 trailrec을 사용할 수 없습니다.
- 오직 JVM 백엔드에서만 꼬리 재귀가 지원됩니다.
