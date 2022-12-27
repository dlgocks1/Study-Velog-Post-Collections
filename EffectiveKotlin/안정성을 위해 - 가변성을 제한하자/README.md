## 왜 가변성을 제한해야 하는가?

- 가변성이 있으면 코드의 실행을 추론하기 어려워진다.
- 멀티스레드 프로그램일 경우에는 적절한 동기화가 필요하다. 변경이 일어나는 지점에서 충돌이 발생가능
- 테스트하기 어렵다.
- 일관성 유지 및 복잡성 증가에 대한 문제가 발생한다.

---

## Kotlin에서 가변성 제한하기

### 1. **읽기 전용 프로퍼티(val) 사용하기**

- 사용자 정의 게터로도 읽기 전용 프로퍼티 val선언이 가능하다.

```
var name = "해찬"
var surname = "이"
val fullname
	get() = "$name $surname"

name = "민수"
print(fullname) // 민수 이
```

    이러한 경우에는 스마트캐스트가 불가능하다.

- 읽기 전용 프로퍼티로 정의해도 Mutable한 데이터를 담고 있다면 내부적으로 변경이 가능하다

- val의 값은 변경될 수 있기는 하지만, 프로퍼티 레퍼런스 자체를 변경할 수는 없다.

### 2. **가변 컬렉션과 읽기 전용 컬렉션 구분하기 **

- 코틀린에서는 읽고 쓸 수 있는 컬렉션과 읽기 전용 컬렉션으로 구분된다.

읽고 쓸 수 있는 컬렉션에서는 Mutable 수식어가 붙는다. ex) MutableList, ArrayList, Mutableset 등등...

- 읽기 전용 컬렉션을 mutable 컬렉션으로 다운캐스팅 금지

![](https://velog.velcdn.com/images/cksgodl/post/2af929d1-2869-4d7a-b332-38b6fcfbee0b/image.png)

```
val list = listOf(1,2,3)

if (list is MutableList) {
	// 이렇게 하면 X
    list.add(4)
}
```

JVM에서는 ArrayList에는 add가 구현되어 있지 않아 UnsupportedOperationException이 발생한다.

만약 읽기 전용 컬렉션을 mutable로 변경해야 한다면 copy를 통해 새로운 mutable 컬렉션을 만들어야한다.

```
list.toMutableList()
```

### 3. **데이터 클래스를 copy하여 사용하기**

Immutable 객체를 사용하면 아래와 같은 장점이 있다.

- 한번 정의된 상태가 유지되므로 코드를 이해하기 쉽다.
- Immutable 객체는 공유시에도 충돌이 발생하지 않아 병렬 처리를 안전하게 할 수 있다.
- Immutable 객체에 대한 참조는 변경되지 않으므로, 쉽게 캐시할 수 있다.
- Immutable 객체의 방어적 복사본을 만들 필요가 없다. 또한 깊은 복사를 따로 할 필요가 없다.
- Immutable 객체는 다른 객체를 만들때 활용하기 좋으며 실행을 더 쉽게 예측할 수 있다.
- Imuutable 객체는 Set 혹은 Map의 키로 활용할 수 있다. (Mutable는 요소에 수정이 일어나면 해시 테이블 내부에서 요소를 찾을 수 없다.)

Mutalbe요소의 해시 테이블 요소의 변경의 예제이다

```
val names: SortedSet<FullName> = TreeSet()
val person = FullName("AAA","AAA")
names.add(person)
names.add(FullName("해찬","이")
names.add(FullName("동현","김")

print(names) // [AAA AAA, 해찬 이, 동현 김]
print(person in names) // true
person.name = "ZZZ"
print(names) // [ZZZ AAA, 해찬 이, 동현 김]]
print(person in names) // false

```

세트 내부에 Person 객체가 있음에도 false를 리턴한다. 해당 객체를 변경하였기 때문에 찾을 수 없는 것이다.

만약 다음과 같은 행위가 true를 반환하게 하려면 새로운 객체를 만들어내어 반환해야한다.

```
class Fullname(
	val name: String,
    val surname: String,
){
	fun changeName(name: String) = Fullname(name, surname)
}
```

다음과 같이 변경하는 메소드를 만들면 새로운 객체가 만들어지기 때문에 위의 식도 true를 반환하게 된다.

하지만 모든 클래스에 이런작업을 하는건 비 효율적이기 때문에 Kotlin에서는 data class에서의 copy를 지원한다.

```
data class Fullname(
	val name: String,
    val surname: String,
)
var name = Fullname("해찬","이")
user = user.copy("해찬","김")
```

### 4. 다른 종류의 변경 가능 지점

다음과 같은 두 리스트를 만들었다.

```
val list1: MutableList<Int> = mutablelistOf()
var list2: List<Int> = listOf()

```

list1은 mutable 컬렉션을 만든 것이고, list2는 var로 읽고 쓸 수 있는 프로퍼티를 만들었다.

두가지 모두 +=연산자를 활용할 수 있지만, 이루어지는 처리는 다르다.

```
list1 += 1 // list1.plusAssing(1)
list2 += 1 // list2 = list2.plus(1)
```

list1은 구체적인 리스트 구현 내부에 변경 가능 지점이 있고,
list2는 프로퍼티 자체가 변경 가능 지점이다. -> 멀티스레드 처리의 안정성이 더 좋다고 할 수 있다.

이처럼 mutable 프로퍼티를 사용하면 사용자 정의 세터 및 델리게이트를 활용해 변경을 추척할 수 있다. mutable 컬렉션도 변경 추적이 가능하나, 추가적인 구현이 필요 따라서 mutable프로퍼티에 읽기 전용 컬렉션을 넣어 사용하는 편이 좋다.
-> 객체를 변경하는 여러 메서드 대신 세터를 사용하고 이를 private로 만들 수도 있기 때문

```
var announcements = listOf<Announcement>)_
	private set
```

최악의 방법은 다음과 같이 프로퍼티와 컬렉션을 모두 변경 가능 지점으로 만드는 것이다.

```
var list3 = mutableListOf<Int>()
```

### 5. 변경 가능 지점 노출하지 않기

상태, State를 나타내는 mutable 객체를 외부에 노출하는 것은 위험하다.

이게 무슨소리냐 다음과 같은 소스를 보자

```
class UserRepository{
	private val storedUsers: MutableMap<Int, String> = mutableMapOf()

    fun loadAll(): MutableMap<Int, String> {
    	return stortedUsers
    }
}
```

다음과 같이 private한 storedUsers를 loadAll의 리턴값으로 넣어버리면 변경 가능 지점을 노출하게 되어 다른 클래스에서 이를 수정할 수 있다.

```
val userRepository = UserREpository()

val storedUsers = userRepository.loadAll()
storedUsers[4] = "민석"
print(userRepository.loadAll()) // {4=민석}

```

이러한 변경 가능 지점 노출을 방지하기 위해 첫번째로는 **방어적 복제**를 활용할 수 있다.

```
class UserHolder {
	private val user: MutableUser()

    fun get(): MutableUser {
    	return user.copy()
    }
}
```

읽기 전용 슈퍼타입으로 업캐스트하여 가변성을 제한할 수도 있다.

```
class UserRepository{
	private val storedUsers: MutableMap<Int, String> = mutableMapOf()

    // 읽기전용 타입으로 변경
    fun loadAll(): Map<Int, String> {
    	return stortedUsers
    }
}
```

### 정리

- var보다는 val을 사용하는 것이 좋다.
- mutable 프로퍼티보다는 imutable 프로퍼티를 사용하는 것이 좋다.
- mutable 객체와 클래스보다는 immutable 객체와 클래스를 사용하는 것이 좋다.
- 변경이 필요한 대상을 만들어야 한다면, immutable 데이터 클래스로 만들고 copy를 활용하는 것이 좋다.
- 컬렉션에 상태를 저장해야 한다면, mutable 컬렉션보다는 읽기 전용 컬렉션을 사용하자.
- 변경 지점을 적절하게 설계하고, 불필요한 변경 지점은 만들지 말자
- mutable 객체를 외부에 노출하지 말자.
