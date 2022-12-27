> Kotlin의 특징 중 하나는 null-safety의 메커니즘으로 인해 Null-Pointer Exception은 Kotlin에서 보기 힘들어 졌다.

하지만 Kotlin이 아닌 Java, C 등의 언어와 협업하여 사용할 때는 예외가 발생할 수 있다.

예를 들어 Spring 서버에서 `List<User>`을 반환하고 nullable과 같은 어노테이션이 붙어있지 않을 때, Kotlin에서는 List 뿐만아니라 User 내의 데이터까지 null이 아니라는 것을 체크해야 한다.

```
public class UserRepo{
	public List<User> getUsers() {
    	// ***
    }
}

// 리스트 뿐만 아니라 리스트 안의 내용까지 null인지 체크해야함
val users: List<Users> = UserRepo().users!!.filterNotNull()
```

리스트는 map, filterNotNull등의 메서드를 제공하지만 제너릭타입이라면 널을 확인하는 것 자체가 눈앞이 깜깜해 질것이다.

> 그래서 코틀린은 타 언어에서 넘어온 타입들을 특수하게 다루는데 이를 **플랫폼 타입**이라고 한다.

### 플랫폼 타입이 뭔데?

플랫폼 타입 -> 타언어에서 전달되어서 nullable인지 아닌지 알 수 없는 타입을 의미한다.

플랫폼 타입은 `String!`처럼 ! 기호를 붙여서 표기한다. 이러한 노테이션이 직접적으로 코드에 나타나진 않는다.

```
val user1 = repo.user 		// User!
val user2 : User= repo.user // User
val user3 : User? = repo.user// User?
```

하지만 들어오는 데이터가 여전히 null일 가능성이 있음으로, NPE는 언제든지 발생할 수 있다.

자바를 코틀린과 함께 사용할 때는 자바 코드에 @Nullable과 @NotNull 어노테이션을 붙여서 사용하길 권장한다고한다.

```
public class UserRepo {
	public @NotNull User getUser(){
   		//...
    }
}
```

또는 여러 어노테이션을 활용하여 파라미터가 null이 아니라는 것을 보장할 수 있다.
ex) JSR 305의 @ParametersAreNonnullByDefault

### 코틀린 코드에서 플랫폼 타입을 최대한 빨리 제거하자.

```
public class JavaClass{
	public String getValue(){
    	return null;
    }
}

// 코틀린
fun statedType() {
	val value: String = JavaClass().value // Error!!
    println(value.length)
}

fun platformType() {
	val value = JavaClass().value
    println(value.length) // Error!!
}

```

두 상황 모두 NPE가 발생하지만, 오류 위치에서 차이가 있다.

`statedType()`에서는 값을 가져오는 위치에서 NPE가 발생한다. 이 위치에서 오류가 발생하면, null이 아니라고 예상을 했지만 null이 나온다는 것을 굉장히 쉽게 알 수 있다. 즉 코드 수정이 용이해진다.

`platformType()`에서는 값을 사용할 때 오류가 난다. 타입 검사기가 이를 검출할 수 없음으로 오류를 찾는 데 오랜 시간이 걸릴 것이다.

> 또한 플랫폼타입 값을 사용하는 다른 코드또한 위험해 질 수 있기때문에, 플랫폼타입은 최대한 빨리 제거하는 것을 권장한다.
