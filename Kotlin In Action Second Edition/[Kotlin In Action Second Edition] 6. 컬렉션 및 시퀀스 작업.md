## 6.1 컬렉션용 함수형 API

함수형 프로그래밍 스타일은 컬렉션을 조작 할 때 많은 이점을 제공한다. 

### 6.1.1 filter 및 map

이 함수를 사용하면 많은 컬렉션 작업을 표현할 수 있다.

아래 예제를 보자.

```kotlin
data class Person(val name: String, val age: Int)

fun main() {
	val list = listOf(1, 2, 3, 4)
	println(list.filter { it % 2 == 0 }) // [2, 4]
}
```
![](https://velog.velcdn.com/images/cksgodl/post/6ecd3e8e-7d1a-4807-8dbb-418862be9460/image.png)

아래는 `map`의 예제이다.

```kotlin
fun main() {
	val list = listof(1, 2, 3, 4) 
    println(list.map { it * it }) // [1, 4, e, 16]
}
```

![](https://velog.velcdn.com/images/cksgodl/post/a08bde8d-5051-44ac-a133-ffe94791a134/image.png)

람다내부의 식은 콜렉션 수 만큼 반복됨으로 성능 개선을 위해선 아래처럼 작성하는 것을 권장한다.

```kotlin
// Bad
people.filter {
    val oldestPerson = people.maxByorNull(Person::age)
    it.age == oldestPerson?.age
}

// Better
val maxAge = people.maxByorNull(Person::age)?.age
people.filter { it.age == maxAge }
```

각각의 API 층마다 콜렉션을 생성함으로 연산 과정을 짧게하면 할수록 좋다.


### 6.1.2 reduce 및 fold

```kotlin
fun main() {
    val list = listOf(1, 2, 3, 4)
    val summed = list.reduce { acc, element ->
        acc + element
    }
    println(summed)
    // 10
    
    val multiplied = list.reduce { acc, element ->
        acc * element
    }
    println(multiplied)
	// 24
}
```

`fold` 함수는 개념적으로는 `reduce`와 매우 유사하지만 컬렉션의 첫 번째 요소 대신 임의의 시작값을 선택할 수 있다.

```kotlin
fun main() {
    val people = listOf(
        Person("Alex", 29),
        Person("Natalia", 28)
    )
    val folded = people.fold("") { acc, person ->
        acc + person.name
	}
    println(folded)
}
	// AlexNatalia
```

숫자 뿐만 아니라 문자열, 객체도 합칠 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/20e45a03-ef4c-4c45-b43f-b309776f5d41/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/5d8a0bea-1d5f-4699-a199-c1410378810b/image.png)


`fold` 또는 `redice` 연산을 사용하여 간결하게 표현할 수 있는 알고리즘이 많이 있다. 

`fold` 또는 `reduce` 연산에서 간헐적으로 발생하는 모든 값을 검색하려는 경우 `runningReduce`와 `runningFold` 함수가 유용하다. `fold`, `reduce`와의 차이점은 이 함수는 리스트를 반환한다는 점이다. 최종 결과와 함께 모든 누산값이 포함된다.

```kotlin
fun main() {
    val list = listOf(1, 2, 3, 4)
    val summed = list.runningReduce { acc, element ->
        acc + element
    }
    println(summed) // [1, 3, 6, 10]
    
    val multiplied = list.runningReduce { acc, element ->
        acc * element
    }	
	println(multiplied) //[1,2,6,24]
    
	val people = listOf(
        Person("Alex", 29),
        Person("Natalia", 28)
    )
    println(people.runningFold("") { acc, person ->
        acc + person.name
	})
    // [, Alex, AlexNatalia]
}
```

### 6.1.3 all, any, none, count, find

코틀린에서 또 다른 일반적인 작업은 컬렉션의 요소가 특정 조건과 일치하는지, 일부만 일치하는지 또는 전혀 일치하지 않는지 확인할 수 있다는 것이다.

```kotlin
val canBeInClub27 = { p: Person -> p.age <= 27 }

fun main() {
    val people = listOf(Person("Alice", 27), Person("Bob", 31))
    println(people.all(canBeInClub27)) // 모두 일치 하는 지 
    // false
    
    println(people.any(canBeInClub27)) // 하나라도 일치하는 지
    // true
}
```

`!.all()`은 `any`로 대체할 수 있다.

```kotlin
fun main() {
    val list = listOf(1, 2, 3)
    println(!list.all { it == 3 })
    // true
    println(list.any { it != 3 })
    // true
}
```

술어를 만족하는 요소의 수를 알고 싶으면 `count`를 사용한다.

```kotlin
fun main() {
	val people = listof(Person("Alice", 27), Person("Bob", 31)) 	
    println(people.count(canBeInClub27))
	// 1
}
```

> count vs filter 사이즈 비교
컬렉션을 필터링하고 크기를 구하면 개수를 잊어버리고 구현하기 쉽다.
```kotlin
println(people.filter(canBeInClub27).size) // 1
```
하지만 이 경우 술어를 만족하는 모든 요소를 저장하기 위해 중간에 컬렉션이 생성된다. 반면 카운트 방식은 요소 자체가 아닌 일치하는 요소의 수만 추적하므로 더 효율적이다. 

### 6.1.4 partition

컬렉션을 조건을 충족하는 요소와 그렇지 않은 요소의 두 그룹으로 나눠야 할때가 있다. `filter`, `filterNot`을 사용하여 이 두 목록을 만들 수 있다.

```kotlin
fun main() {
 	val canBeInClub27 = { p: Person -> p.age <= 27 }
    
    val people = listof(
    	Person("Alice", 26),
    	Person("Bob", 2e),
    	Person("Carol", 31)
	)
	val comeIn = people.filter(canBeInClub27)
	val stayout = people.filterNot(canBeInClub27) println(comeIn)
	// [Person(name=Alice, age=26)]
	println(stayout)
	// [Person(name=Bob, age=2e), Person(name=Carol, age=31)]
}
```

하지만 위의 방법보다 `partition`을 활용하는 더 간결한 방법도 있다. 이 함수는 술어를 반복할 필요도 없고 입력 컬렉션을 두 번 반복할 필요도 없이 이 목록 쌍을 반환한다.

```kotlin
val (comeIn, stayOut) = people.partition(canBeInClub27)
println(comeIn)
// [Person(name=Alice, age=26)]
println(stayOut)
// [Person(name=Bob, age=29), Person(name=Carol, age=31)]
```

![](https://velog.velcdn.com/images/cksgodl/post/1ed05d6e-6752-4d77-8d3d-e17d89d1d01c/image.png)

구현체는 다음과 같다.

```kotlin
public inline fun <T> Iterable<T>.partition(predicate: (T) -> Boolean): Pair<List<T>, List<T>> {
    val first = ArrayList<T>()
    val second = ArrayList<T>()
    for (element in this) {
        if (predicate(element)) {
            first.add(element)
        } else {
            second.add(element)
        }
    }
    return Pair(first, second)
}
```

### 6.1.5 groupBy

컬렉션의 요소를 파티션 반환을 통해 '참' 및 '거짓' 그룹으로만 클러스터링할 수 없는 경우가 많다. 대신 모든 요소를 특정 품질에 따라 다른 그룹으로 나누고 싶을 수 있다.

```kotlin
fun main() {
	val people = listof(
		Person("Alice", 31),
        Person("Bob", 2e),
        Person("Carol", 31)
	)
	println(people.groupBy { it.age })
}
```

![](https://velog.velcdn.com/images/cksgodl/post/68c52491-6abb-43f4-994d-d3e8565edb23/image.png)

각 그룹은 맵에 저장되므로 결과 유형은 `Map<Int, List<Person>>`이다.

`mapKeys` 및 `mapValues`와 같은 함수를 사용하여 이 맵을 추가로 수정할 수 있다.


### 6.1.6 associate, associateWith, 및 associateBy

요소를 그룹화하지 않고 컬렉션의 요소로 맵을 만들고 싶다면 `associate` 함수를 사용하면 된다. `associate` 함수를 사용하여 다른 `Map<String, Int>`에서와 마찬가지로 `Person` 객체 목록을 나이에 따른 이름의 맵으로 바꾸고 예제 값을 쿼리한다.

```kotlin
fun main() {
	val people = listof(Person("Joe", 22), Person("Mary", 31)) 
    val nameToAge = people.associate { it.name to it.age } 
    
    println(nameToAge)
	// {Joe=22, Mary=31}
	println(nameToAge["Joe"])
	// 22
```

![](https://velog.velcdn.com/images/cksgodl/post/8ece1b33-3641-4530-8f76-aa70633dbd37/image.png)

```kotlin
  fun main() {
       val people = listOf(
           Person("Joe", 22),
           Person("Mary", 31),
           Person("Jamie", 22)
       )
       val personToAge = people.associateWith { it.age }
       println(personToAge)
       // {Person(name=Joe, age=22)=22, Person(name=Mary, age=31)=31,
       //  Person(name=Jamie, age=22)=22}
       
       val ageToPerson = people.associateBy { it.age }
       println(ageToPerson)
       // {22=Person(name=Jamie, age=22), 31=Person(name=Mary, age=31)}
}
```

변환 함수로 인해 동일한 키가 여러 번 추가되는 경우 마지막 결과가 이전 값을 덮어쓴다.

### 6.1.7 replaceAll and fill

`Kotlin` 표준 라이브러리에는 컬렉션의 내용을 변경하는데 도움이 되는 몇 가지 편의 함수가 포함되어 있다. 

`MutableList`에 적용하면 `replaceAll` 함수는 목록의 각 요소를 사용자가 지정한 람다의 결과로 바꾼다.

모든 요소를 동일한 값으로 바꾸는 특수한 경우에는 `fill` 함수를 사용할 수 있다.

```kotlin
fun main() {
    val names = mutableListOf("Martin", "Samuel")
    println(names)
    // [Martin, Samuel]
    names.replaceAll { it.uppercase() }
    println(names)
    // [MARTIN, SAMUEL]
    names.fill("(redacted)")
    println(names)
    // [(redacted), (redacted)]
}
```

### 6.1.8 ifEmpty

입력 컬렉션이 비어 있지 않은 경우, 즉 처리할 실제 요소가 있는 경우에만 프로그램을 진행하는 것이 합리적일 때가 많다. 

`ifEmpty` 함수를 사용하면 컬렉션에 요소가 포함되지 않은 경우 기본값을 생성하는 람다를 제공할 수 있다.

```kotlin
fun main() {
   val empty = emptyList<String>()
   val full = listOf("apple", "orange", "banana")
   println(empty.ifEmpty { listOf("no", "values", "here") })
   // [no, values, here]
   println(full.ifEmpty { listOf("no", "values", "here") })
   // [apple, orange, banana]
}
```

> `ifBlank`: 문자열에 대한 `ifEmpty`의 형제 함수
텍스트로 작업할 때 공백 문자로만 구성된 문자열 은 순수한 빈 문자열보다 표현력이 떨어지는 경우가 많기 때문에 '비어 있음'이라는 요건을 '공백'으로 완화하는 경우가 있다. 
```kotlin
fun main() {
	val blankName = " " 
    val name = "J. Doe"
	println(blankName.ifEmpty { "(이름 없음)" }) 	 
    // 
	println(blankName.ifBlank { "(이름 없음)" }) `	
    // (이름 없음)
	println(name.ifBlank { "(이름 없음)" })
	// J. Doe
}
```

### 6.1.9 chunked and windowed

컬렉션의 데이터가 일련의 정보를 나타내는 경우, 한 번에 여러 개의 연속된 값으로 작업하고 싶을 수 있다. 

```kotlin
fun main() {
    println(temperatures.windowed(3))
    // [[27.7, 29.8, 22.0], [29.8, 22.0, 35.5], [22.0, 35.5, 19.1]]
    println(temperatures.windowed(3) { it.sum() / it.size })
    // [26.5, 29.099999999999998, 25.53333333333333]
}
```

![](https://velog.velcdn.com/images/cksgodl/post/de7a8156-864f-4f41-9f4d-8958c40b1188/image.png)

입력 컬렉션 위에 슬라이딩 창을 띄우는 대신 컬렉션을 주어진 크기의 개별 부분으로 나누고 싶을 수 있다. `chunk` 함수를 사용하면 이를 달성할 수 있다.

```kotlin
fun main() {
	println(temperatures.chunked(2))
	// [[27.7, 2e.8], [22.0, 35.5], [1e.1]] 	
	println(temperatures.chunked(2) { it.sum() }) 
    // [57.5, 57.5, 1e.1]
}
```

![](https://velog.velcdn.com/images/cksgodl/post/788f2840-ebc4-4199-b2f1-65dd4dbd0c9a/image.png)

### 6.1.10 컬렉션 병합: zip

때로는 관련 데이터가 포함된 별도의 목록으로 작업하고 이 정보를 집계해야 할 수도 있다. 

`zip` 함수를 사용하여 두 컬렉션의 동일한 인덱스에 있는 값으로 쌍의 목록을 만들 수 있다. 함수에 람다를 전달하면 출력이 어떻게 변환될지 지정할 수도 있다. 

```kotlin
fun main() {
    val names = listOf("Joe", "Mary", "Jamie")
    val ages = listOf(22, 31, 31, 44, 0)
    println(names.zip(ages))
    // [(Joe, 22), (Mary, 31), (Jamie, 31)]
    println(names.zip(ages) { name, age -> Person(name, age) })
    // [Person(name=Joe, age=22), Person(name=Mary, age=31), Person(name=Jamie, age=31)]
}
```

![](https://velog.velcdn.com/images/cksgodl/post/f09e2326-0baa-488f-8d90-64d00a926931/image.png)

> 결과 컬렉션의 크기는 두 목록 중 더 짧은 목록과 동일하다는 점에 유의하라.

쌍 객체를 생성하는 `to` 함수와 마찬가지로 `zip` 함수는 인픽스 함수로도 호출할 수 있지만, 이 경우 변환 람다를 전달할 수 없다.

### 6.1.11 flatMap 및 flatten

```kotlin
class Book(val title: String, val authors: List<String>)

val library = listOf(
	Book("Kotlin in Action", listOf("Isakova", "Elizarov", "Aigner", "Jemerov")), 	
    Book("Atomic Kotlin", listOf("Eckel", "Isakova")),
	Book("The Three-Body Problem", listOf("Liu"))
)
```

라이브러리의 모든 작성자를 계산하려면 `map`을 사용하여 계산할 수 있다.

```kotlin
 fun main() {
 	val authors = library.map { it.authors }
    println(authors)
    // [[Isakova, Elizarov, Aigner, Jemerov], [Eckel, Isakova], [Liu]]
}
```

`authors`는 `List<List<String>>`으로 반환된다. 

```kotlin
fun main() {
    val authors = library.flatMap { it.authors }
    println(authors)
    // [Isakova, Elizarov, Aigner, Jemerov, Eckel, Isakova, Liu]
    println(authors.toSet())
    // [Isakova, Elizarov, Aigner, Jemerov, Eckel, Liu]
}
```

`flatMap` 함수를 사용하면 별도의 중첩 없이 라이브러리에 있는 모든 저작자의 집합을 계산할 수 있다. 먼저 인자로 주어진 함수에 따라 각 요소를 컬렉션으로 변환(또는 매핑)한 다음(맵 함수에서 본 것처럼) 이러한 목록을 하나로 결합(또는 평탄화)한다.

## 6.2 지연 수집 작업: Sequence

시퀀스는 이러한 계산을 수행할 수 있는 다른 방법으로, Java 8의 스트림과 유사하게 중간 임시 객체 생성을 피할 수 있다.

```kotlin
people.map(Person::name).filter { it.startsWith("A") }
```

`Kotlin` 표준 라이브러리 참조에 따르면 맵과 필터는 모두콜렉션을 반환한다. 즉, 일련의 호출은 맵 함수의 결과를 담는 목록과 필터의 결과를 담는 목록, 두 개의 목록을 생성한다. 

소스 목록에 두 개의 요소가 포함되어 있을 때는 문제가 되지 않지만, 목록이 백만개라면 효율성이 훨씬 떨어진다.

```kotlin
people
    .asSequence()
	.map(Person::name)
	.filter { it.startsWith("A") }
	.toList()
```

모든 컬렉션은 확장 함수 `asSequence`를 호출하여 시퀀스로 변환할 수 있다. 시퀀스에서 일반목록으로 반대변환을 하려면`toList`를 호출하면 된다.

### 6.2.1 시퀀스 연산 실행하기: 중간 및 터미널 작업

시퀀스에 대한 연산은 중간과 종결의 두 가지 범주로 나뉜다. 중간 연산은 다른 시퀀스를 반환하는데, 이 시퀀스는 콜렉션을 반환한다.

![](https://velog.velcdn.com/images/cksgodl/post/c8281bdc-b527-4ce0-a4da-c0183e2cabaa/image.png)

```kotlin
fun main() {
    println(
        listOf(1, 2, 3, 4)
            .asSequence()
            .map {
                print("map($it) ")
                it * it
            }.filter {
                print("filter($it) ")
                it % 2 == 0
	} )
    // kotlin.sequences.FilteringSequence@506e1b77
}
```

터미널 연산(`toList`)은 모든 연기된 계산을 수행한다.

주목해야 할 또 한 가지 중요한 점은 연산이 수행되는 순서이다. 콜렉션의 기본 접근 방식은 각 요소에 대해 맵 함수를 먼저 호출한 다음 결과 시퀀스의 각 요소에 대해필터 함수를 호출하는 것이다.

이는 컬렉션에서는 맵과 필터가 작동하지만 시퀀스에서는 작동하지 않는 방식이다. 시퀀스의 경우 모든 작업이 각 요소에 순차적으로 적용된다. (첫 번째 요소를 처리(매핑한 다음 필터링)한 다음 두 번째 요소를 처리하는 식) 

이 접근 방식은 결과에 도달하기 전에 결과가 얻어지면 일부 요소가 전혀 변환되지 않음을 의미한다. 

```kotlin
fun main() {
    println(
	    listOf(1, 2, 3, 4)
    	    .asSequence()
			.map { it * it }
			.find { it > 3 }
	) // 4
)
```

시퀀스 대신 컬렉션에 동일한 연산을 적용하면 먼저 맵의 결과가 평가되어 초기 컬렉션의 모든 요소가 변환된다. 시퀀스의 경우 지연 접근 방식을 사용하면 일부 요소의 처리를 건너 뛸 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/eec49deb-02a2-4786-8b17-ec065ca8a369/image.png)

컬렉션에서 수행하는 작업의 순서도 성능에 영향을 줄 수 있다. `Person` 컬렉션이 있는데 이름이 특정 제한보다 짧은 경우 그 이름을 인쇄하고 싶다고 가정해 보겠다. 각 사람을 이름에 매핑한 다음 너무 긴 이름을 필터링하는 두 가지 작업을 수행해야 한다.

이 경우 매핑 및 필터 작업을 어떤 순서로든 적용할 수 있다. 두 가지 접근 방식은 동일한 결과를 제공하지만 수행해야 하는 총 변환 횟수에서 차이가 있다.

```kotlin
fun main() {
    val people = listOf(
        Person("Alice", 29),
        Person("Bob", 31),
        Person("Charles", 31),
        Person("Dan", 21)
	) 
    println(
        people
            .asSequence()
            .map(Person::name)
            .filter { it.length < 4 }
            .toList()
    )
    // [Bob, Dan]
    
    println(
        people
            .asSequence()
			.filter { it.name.length < 4 }
			.map(Person::name)
			.toList()
	)
    // [Bob, Dan]
}
```

![](https://velog.velcdn.com/images/cksgodl/post/ee0cf887-fd35-4c01-a4f0-a4e7c4711c16/image.png)

필터를 먼저 적용하면 부적절한 요소는 가능한 한 빨리 필터링되어 변환되지 않는다. 경험상 작업 체인에서 요소를 더 일찍 제거할수록(물론 코드의 논리를 손상시키지 않고) 코드의 성능이 향상된다.

### 6.2.2 시퀀스 만들기

이전 예제에서는 컬렉션에서 `asSequence()`를 호출하여 시퀀스를 생성하는 동일한 방법을 사용했다. 또 다른 방법은 생성 시퀀스 함수를 사용하는 것이다. 이 함수는 이전 요소가 주어지면 시퀀스의 다음 요소를 계산할 수 있다. 

```kotlin
fun main() {
	val naturalNumbers = generateSequence(0) { it + 1 } 
    val numbersTo100 = naturalNumbers.takeWhile { it <= 100 } 
    println(numbersTo100.sum())
	// 5050
}
```

다시 한 번 첫 번째 요소와 각 후속 요소를 가져오는 방법을 제공하여 시퀀스를 생성한다. `any`를 `find`로 대체하면 숨겨진 파일이 어딘가에 있음을 나타내는 부울 값 대신 숨겨진 실제 디렉터리를 얻을 수 있다.

```kotlin
import java.io.File

fun File.isInsideHiddenDirectory() =
        generateSequence(this) { it.parentFile }.any { it.isHidden }

fun main() {
    val file = File("/Users/svtk/.HiddenDir/a.txt")
    println(file.isInsideHiddenDirectory())
    // true
}
```

## 요약

- `filter` 및 `map` 기능은 컬렉션 조작의 기초를 형성하며 특정 술어와 일치하는 요소를 추출하거나 요소를 새로운 형태로 변환하는 작업을 쉽게 수행할 수 있도록 해준다.
- `fold` 및 `reduce` 작업은 컬렉션의 정보를 집계하여 항목 컬렉션이 주어진 단일값 을 계산하는데 도움이 된다.
- 연관 및 그룹별 함수를 사용하면 평면 목록을 맵으로 변환하여 자신만의 기준에 따라 데이터를 구조화할 수 있다.
- 인덱스로 연관된 컬렉션의 데이터의 경우 `chunk`, `window` 및 `zip` 함수를 사용하여 컬렉션 요소의 하위 그룹을 만들거나 여러 컬렉션을 병합할 수 있다.
- 술어, 부울을 반환하는 람다 함수, `all`, `any`, `none` 및 기타 형제 함수를 사용하면 특정 불변수가 컬렉션에 적용되는지 여부를 확인할 수 있다.
- 중첩된 컬렉션을 처리하기 위해 `flatten` 함수를 사용하면 중첩된 항목을 추출할 수 있으며, `flatMap` 함수를 사용하면 같은 단계에서 변환을 수행할 수 도 있다.
- 시퀀스를 사용하면 중간 결과를 보관하기 위해 컬렉션을 만들지 않고도 컬렉션에서 여러 작업을 느리게 결합할 수 있으므로 코드의 효율성이 높아진다. 컬렉션에 사용하는 것과 동일한 함수를 사용하여 시퀀스를 조작할 수 있다.

