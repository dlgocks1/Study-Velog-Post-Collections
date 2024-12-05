* TDD기반 개발을 진행하라
* 테스트코드 작성에 정성을 다해라.

등의 테스트코드에 대한 중요성을 정말 여러곳에서 들을 수 있었다. 하지만 안드로이드 개발을 진행하며 테스트 코드를 작성해본 적이 손에 꼽을 정도로 적어 한번 안드로이드에서의 테스트 코드를 작성해보고자 한다.

## 단위테스트와 UI테스트

> 단위 테스트는 응용 프로그램에서 테스트 가능한 가장 작은 소프트웨어를 실행하여 예상대로 동작하는지 확인하는 테스트이다. 

단위 테스트에서 테스트 대상 단위의 크기는 엄격하게 정해져 있지 않지만, 일반적으로 클래스 또는 메소드 수준으로 작은 테스트를 의미한다.

> UI 테스트는 애플리케이션의 사용자 인터페이스 (UI)를 테스트하는 과정이다. 지정된 시나이로에 따라 기능을 테스트하고 UI 동작을 확인한다. 

지금까지 개발하며 거의 모든테스트를 수동으로 진행하였고 많은 시간이 소요됬다. 하지만 자동화된 테스트도구를 이용하면 코드 변경 후 어플리케이션이 제대로 동작하는지 확인하기 위해서 유용하다.
안드로이드에서는 `Espresso`, `Robolectric`등 다양한 UI 테스트 도구를 제공하지만 이번 글에서는 `androidx.compose.ui.test.junit4`를 활용할 예정이다.

---

# Compose에서의 UI 테스트 🧪

`androidx.compose.ui.test.junit4` 내부의 함수들을 활용해 UI테스트를 진행해보고자 한다.

## Semantics 🗃️ 

![](https://velog.velcdn.com/images/cksgodl/post/ecbb0fe5-849c-4e4a-b724-57fd75bb90e6/image.png)

컴포즈에서 컴포지션은 앱의 `UI`를 설명하고 컴포저블을 실행하여 생성된다.  컴포지션은 `UI`를 설명하는 컴포저블로 구성된 트리 구조이다.
테스트에서는 이 트리를 사용하여 앱과 상호작용하고 이에 관한 `assertion`을 만든다.  컴포저블의 `시맨틱 의미`에 관한 정보는 이 트리에 포함되어있다.

~~라고 `안드로이드 디벨로퍼`에서 설명하고 있지만 무슨 소리인지 당최 알아먹을 수 없다.~~
> 컴포즈에서는 컴포지션을 통해 `UI Tree`가 생성되고 각각의 그려진 컴포저블에게 의미가 담긴 속성(시맨틱)이 부여된다. 이를 통해 테스트 프레임워크에서 뷰에 접근하고 테스트를 할 수 있는 것이다.

## 시멘틱 속성의 예제 👏

시맨틱 속성들에는 컴포저블의 의미를 전달하는 속성이 포함되어 있다.
예를 들어 `Text`컴포저블에서는 `text`가, `Icon`에는 `contentDescription`속성이 포함될 수 있다.


`Layout Inspector`를 통해 속성을 시각적으로 볼 수 있으며 스위치의 시맨틱 노드는 다음과 같다.
![](https://velog.velcdn.com/images/cksgodl/post/c3f3d81d-9c7c-46d6-9ac3-67176dcf23de/image.png)

## 시멘틱 속성을 통해 노드를 찾고 테스트해보자 🍄

이러한 스위치의 `시맨틱 노드`를 활용하여 노드를 찾아 상호작용하고 테스트할 수 있다.

예제와 같이 어떻게 뷰(노드)를 찾고 이를 테스트하는지 알아보자. 다음은 스위치가 `off`상태인지 확인하는 소스이다.
```
val mySwitch = SemanticsMatcher.expectValue(
    SemanticsProperties.Role, Role.Switch
)
composeTestRule.onNode(mySwitch)
    .performClick()
    .assertIsOff()
```


#### `onNode`함수란 무엇인가??

```
fun onNode(
	matcher: SemanticsMatcher,
    useUnmergedTree: Boolean = false
): SemanticsNodeInteraction
```

> `onNode` 함수는 `androidx.compose.ui.test.junit4.ComposeTestRule` 클래스에 포함되어 있는 함수이다. `Compose UI Testing`을 위한 함수이며, `시멘틱매처`를 통해 뷰를 찾을 수 있다.

`onNode`함수 내부웨서는 인자로 `SemanticsMatcher` 클래스를 통해 원하는 노드를 찾을 수 있다.


`sementicsMatcher.expectValue`는 다음과 같다. 
```
fun <T> expectValue(key: SemanticsPropertyKey<T>, expectedValue: T): SemanticsMatcher {
	return SemanticsMatcher("${key.name} = '$expectedValue'") {
    	it.config.getOrElseNullable(key) { null } == expectedValue
	}
}
```
`key`값으로는 `SemanticsPropertyKey`의 값을, `value`값으로는 해당 값을 넣으면 된다. 
또한 `inline fun`으로 `and`, `or` 및 `not`, `matches`, `matchesAny`등을 제공하고 있음으로 이를 활용해 특정 뷰를 찾아 테스트할 수 있다.


```
val mySwitch = SemanticsMatcher.expectValue(
    SemanticsProperties.Role, Role.Switch
)

val myTag = SemanticsMatcher.expectValue(
    SemanticsProperties.TestTag, "TestTag"
)

// Switch역할을 수행하며, 태그가 `TestTag`인 뷰가 있는지 확인한다.
composeTestRule.onNode(mySwitch and myTag).assertDoesNotExist() 
```

이러한 `sementicsMatcher`을 직접 입력할 수도 있고 `Junit4`에서는 수 많은 매쳐를 함수로 감싸서 제공해주고 있다.

```
fun hasTestTag(testTag: String): SemanticsMatcher =
    SemanticsMatcher.expectValue(SemanticsProperties.TestTag, testTag)
    
fun isToggleable(): SemanticsMatcher =
    hasKey(SemanticsProperties.ToggleableState)

fun isFocused(): SemanticsMatcher =
    SemanticsMatcher.expectValue(SemanticsProperties.Focused, true)

fun hasText(
    text: String,
    substring: Boolean = false,
    ignoreCase: Boolean = false
): SemanticsMatcher {
	// ...
}

// 원하는 함수들을 조합해 노드를 찾기
composeTestRule.onNode(hasTestTag("Button") and hasNoClickAction()).assertExists()
```

또한 `onNoe`함수 뿐만 아니라 
* `onNodeWithContentDescription`
* `onNodeWithTag`
* `onNodeWIthText`
* `onRoot`

등을 통해 노드를 찾는 확장함수도 제공한다.

```
composeTestRule.onNodeWithTag("Test Button2").performClick()
composeTestRule.onNodeWithText("Clicked!").assertExists()
composeTestRule.onNodeWithContentDescription("IMG_PROFILE").assertExists()
```

## `composeTestRule`란? 🤔

위에서 부터 계속 `composeTestRule`이라는 것을 사용했는데 이는 무엇일까?

```
@get:Rule
val composeTestRule = createComposeRule()
```

> `createComposeRule()`은 `AndroidX` 테스트 라이브러리에서 제공하는 `Compose UI` 테스트를 위한 `Rule`이다.

`createComposeRule()` 함수를 사용하면 `Compose UI` 테스트를 위한 테스트 환경을 빠르고 쉽게 설정할 수 있다. 

_이 `Rule`은 `@Before` 메서드에서 자동으로 `Compose UI` 테스트 환경을 설정하고, `@After` 메서드에서 자동으로 리소스를 해제한다._

특정 액티비티를 지정하고 싶다면 `createAndroidComposeRule<ACTIVITY_NAME>()` 을 통해 생성할 수 있다.

> `createComposeRule`은 테스트 시작전 `Compose UI`환경을 자동으로 설정해 주고 테스트가 끝났을 때 자동으로 리소스를 해제해준다.

## 테스트룰을 적용해 뷰를 그리고 테스트하자. 👍

```
class ExampleComposeTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testButton() {
        // Composable 함수를 호출하여 UI를 작성합니다.
        composeTestRule.setContent {
            MyScreenContent()
        }
       
		// 작성된 뷰의 노드를 찾고 이를 테스트합니다.
    	composeTestRule.onNodeWithTag("Text Field").assertExists()

	}
}
```

`assert` 함수를 통해 해당 노드를 테스트한다.  

#### 다음은 노드의 상태를 테스트하기 위한 `assert`함수들이다.

```
assertDoesNotExist : 트리 구조에 노드가 존재하지 않는지 테스트한다.
assertExists : 트리에 노드가 존재하는지 테스트한다.

assertIsDisplayed : 노드가 현재 화면에 그려지는지 테스트한다.
assertIsNotDisplayed : 노드가 현재 화면에 그려지지 않는지 테스트한다.

assertIsEnabled : 노드가 현재 활성화 상태인지 테스트한다.
assertIsNotEnabled : 노드가 현재 비활성화 상태인지 테스트한다.
노드가 enable 시멘틱 속성을 가지고있지 않으면 에러

assertIsOn : 노드가 현재 체크 상태인지 테스트한다.
assertIsOff : 노드가 현재 체크 상태가 아닌지 테스트한다.
노드가 toggleable하지 않으면 에러

assertIsSelected : 노드가 현재 선택 상태인지 테스트한다.
assertIsNotSelected : 노드가 현재 선택되지 않은 상태인지 테스트한다.
노드가 selectable하지 않으면 에러

assertIsToggleable : 노드가 토글인지 테스트한다.
assertIsSelectable : 노드가 선택가능한지 테스트한다.

assertIsFocused : 노드가 포커스 상태인지 테스트한다.
assertIsNotFocused : 노드가 포커스 상태가 아닌지 테스트한다.

assertContentDescriptionEquals(vararg values: String)
	: 노드의 ContentDescription과 동일한지 테스트한다.
assertContentDescriptionContains 
	: 노드의 ContentDescription을 포함하는지 테스트한다.
    
assertTextEquals : 노드(Text, EditableText)가 해당 텍스트와 동일한지 테스트한다.
assertTextContains : 노드(Text, EditableText)가 해당 텍스트를 가지는지 테스트한다.
    
assertValueEquals : 노드의 StateDescription과 동일한지 테스트한다.
assertRangeInfoEquals : 노드의 ProgresBar과 동일한지 테스트한다.

assertHasClickAction : 노드가 클릭액션을 가지고 있는지 테스트한다.
assertHasNoClickAction : 노드가 클릭액션이 없는지 테스트한다.


assert(matcher: SemanticsMatcher) : 매쳐를 만족하는지 테스트한다.
assertCountEquals(expectedSize: Int) : 노드의 결과가 갯수와 동일한지 테스트한다.
assertAny(matcher : SemantisMatcher) : 어떤 매쳐라도 만족하는지 테스트한다.
assertAll(matcher : SemanticsMatcher) : 모든 매쳐가 만족하는지 테스트한다.
```

#### 다음은 노드의 크기를 테스트하기 위한 assert함수들이다.

```
assertWidthIsEqualTo(expectedWidth: Dp) 
assertTouchWidthIsEqualTo(expectedWidth: Dp) : 가로 터치 넓이가 동일한지 테스트한다.

assertHeightIsEqualTo(expectedHeight: Dp)
assertTouchHeightIsEqualTo(expectedHeight: Dp) : 세로 터치 넓이가 동일한지 테스트한다.

assertPositionInRootIsEqualTo(
    expectedLeft: Dp,
    expectedTop: Dp
) : 루트 포지션으로 부터 상대위치를 테스트한다.

// 등등,,,
```


#### 다음은 노드의 액션을 정의하기 위한 함수들이다.
```
// Actions
performClick : 노드를 클릭한다.
performScrollTo : 노드를 스크롤한다.
scrollToNode : 지정 노드까지 스크롤한다.
performScrollToIndex : 스크롤가능한 콘테이너에서 해당 자식위치까지 스크롤한다.
performScrollToKey : 해당 키값까지 스크롤한다.
performScrollToNode : 스크롤 가능한 콘테이너에서 해당 노드까지 스크롤한다.
performGesture : 제스처이벤트를 실행한다.
performTouchInput : 터치이벤트를 실행한다.
performMouseInput : 마우스이벤트를 실행한다.

// TextActions
performTextClearance : 텍스트를 클리어한다.
performTextInput : 텍스트를 입력한다.
performTextInputSelection : 텍스트 Selection을 선택한다.
performTextReplacement : 텍스트를 수정한다.
performIMEAction : IME액션을 실행한다.

등등...
```


이렇게 첫 번째 `Compose UI`테스트가 성공하였다.
![](https://velog.velcdn.com/images/cksgodl/post/1585e4ba-7fcd-4d46-909f-bd271798f43c/image.png)


## TDD기반으로 로그인 페이지 작성해보기

요구사항 기능은 다음과 같다.
```
아이디 비밀번호를 입력받는다.
1. 아이디는 7글자 이상이어야 한다.
2. 비밀번호는 숫자, 영어, 특수문자를 하나이상씩 포함하고 8글자 이상이어야 한다.
```

위의 요구된 제시사항대로 먼저 테스트 코드를 작성한다.
```
class LoginIdPasswdScreenTest {

	@get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun `아이디가_7글자_이하이면_로그인버튼이_비활성화된다`() {
        composeTestRule.setContent {
            LoginIdPasswdScreen()
        }
        composeTestRule.onNodeWithTag(testTag = "ID_TEXT_FIELD")
            .performTextInput("123456")
        composeTestRule.onNodeWithTag(testTag = "PASSWD_TEXT_FIELD")
            .performTextInput("123456123a@s")
        composeTestRule.onNodeWithText("로그인").assertIsNotEnabled()
    }

    @Test
    fun `비밀번호에_특수문자가_없으면_로그인버튼이_비활성화된다`() {
        composeTestRule.setContent {
            LoginIdPasswdScreen()
        }
        composeTestRule.onNodeWithTag(testTag = "ID_TEXT_FIELD")
            .performTextInput("123456")
        composeTestRule.onNodeWithTag(testTag = "PASSWD_TEXT_FIELD")
            .performTextInput("12345612as")
        composeTestRule.onNodeWithText("로그인").assertIsNotEnabled()
    }

    @Test
    fun `비밀번호에_문자가_없으면_로그인버튼이_비활성화된다`() {
        composeTestRule.setContent {
            LoginIdPasswdScreen()
        }
        composeTestRule.onNodeWithTag(testTag = "ID_TEXT_FIELD")
            .performTextInput("123456")
        composeTestRule.onNodeWithTag(testTag = "PASSWD_TEXT_FIELD")
            .performTextInput("12345612@@@@#")
        composeTestRule.onNodeWithText("로그인").assertIsNotEnabled()
    }

    @Test
    fun `비밀번호에_숫자가_없으면_로그인버튼이_비활성화된다`() {
        composeTestRule.setContent {
            LoginIdPasswdScreen()
        }
        composeTestRule.onNodeWithTag(testTag = "ID_TEXT_FIELD")
            .performTextInput("123456")
        composeTestRule.onNodeWithTag(testTag = "PASSWD_TEXT_FIELD")
            .performTextInput("asdasdadasd@@@@#")
        composeTestRule.onNodeWithText("로그인").assertIsNotEnabled()
    }

    @Test
    fun `비밀번호가_8자_미만이면_로그인버튼이_비활성화된다`() {
        composeTestRule.setContent {
            LoginIdPasswdScreen()
        }
        composeTestRule.onNodeWithTag(testTag = "ID_TEXT_FIELD")
            .performTextInput("1234567")
        composeTestRule.onNodeWithTag(testTag = "PASSWD_TEXT_FIELD")
            .performTextInput("1234a@b")
        composeTestRule.onNodeWithText("로그인").assertIsNotEnabled()
    }

    @Test
    fun `아이디와_비밀번호가_모두_형식에_맞다면_로그인버튼이_활성화된다`() {
        composeTestRule.setContent {
            LoginIdPasswdScreen()
        }
        composeTestRule.onNodeWithTag(testTag = "ID_TEXT_FIELD")
            .performTextInput("1234567")
        composeTestRule.onNodeWithTag(testTag = "PASSWD_TEXT_FIELD")
            .performTextInput("123123asd@#")
        composeTestRule.onNodeWithText("로그인").assertIsEnabled()
    }

}
```

일단 생각할 수 있는 정도의 예외 케이스만을 작성하고 코드를 작성한다. 
_지금 보니 이정도의 코드는`UI 테스트`가 아닌 `유닛 테스트`에 작성하는 것이 맞는 것 같다는 생각이 든다._

작성한 테스트코드를 기반으로 실제 UI를 작성하여 보자.

```
val PASSWD_REGEX =
    Regex("""^(?=.*[A-Za-z])(?=.*\d)(?=.*[@${'$'}!%*#?&])[A-Za-z\d@${'$'}!%*#?&]{8,}${'$'}""")

@Composable
fun LoginIdPasswdScreen() {

    var id by remember { mutableStateOf("") }
    var passwd by remember { mutableStateOf("") }

    Column(modifier = Modifier.fillMaxSize()) {
        LoginIdPasswd(
            id = id,
            passwd = passwd,
            updateId = { id = it },
            updatePasswd = { passwd = it }
        )

        Row {
            Text(text = "회원가입")
            Text(text = "비밀번호 찾기")
        }
        Button(onClick = { /*TODO*/ }) {
            Text(text = "카카오 로그인")
        }
        Button(onClick = { /*TODO*/ }) {
            Text(text = "네이버 로그인")
        }
    }
}

@Preview
@Composable
private fun LoginIdPasswd(
    id: String = "",
    passwd: String = "",
    updateId: (String) -> Unit = {},
    updatePasswd: (String) -> Unit = {},
) {
    Text(text = "안녕하세요.\n로즈데이즈입니다.")
    Text(text = "아이디")
    TextField(
        modifier = Modifier.testTag("ID_TEXT_FIELD"),
        value = id,
        onValueChange = updateId,
        label = { Text(text = "아이디") })
    Text(text = "비밀번호")
    TextField(
        modifier = Modifier.testTag("PASSWD_TEXT_FIELD"),
        value = passwd,
        onValueChange = updatePasswd,
        label = { Text(text = "비밀번호") })
    Button(
        onClick = { /*TODO*/ },
        enabled = id.length >= 7 && PASSWD_REGEX.matches(passwd)
    ) {
        Text(text = "로그인")
    }
}
```

![](https://velog.velcdn.com/images/cksgodl/post/698f2cea-2f8e-408f-acd6-d284098e8e3b/image.png)

`아이디`와 `비밀번호`에 따라버튼이 `enable`, `disable` 되는 간단한 뷰를 작성하였다. 

이제 테스트를 진행해 보았다.

![](https://velog.velcdn.com/images/cksgodl/post/364ddccf-41e4-46b7-8f1b-4a856660ca3b/image.gif)

수동으로 아이디 패스워드를 입력하지 않아도 알아서 에뮬레이터를 통해 테스트를 진행해 준다!

![](https://velog.velcdn.com/images/cksgodl/post/d9d3feaf-47d0-4e90-9f1c-d5a11bc03e81/image.png)

이제 `TDD`의 마지막 단계로써 코드의 `중복 코드 제거`, `일반화` 등의 `리팩토링`을 수행하자.

일단 첫 번째 단계로써 컴포즈의 `setContent`를 초기 1회만 실행하도록 변경하자. - 중복제거
```
class LoginIdPasswdScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Before
    fun setUp() {
        composeTestRule.setContent {
            LoginIdPasswdScreen()
        }
    }

}
```

그리고 사용되는 매개변수들을 모두 상수로 추출하자. (`ParameterizedTest`를 이용해도 좋음)

```
companion object {
    const val VERIFIED_ID = "Test1234"
    const val VERIFIED_PASSWD = "123123asd@#"
    const val NOT_VERIFIED_ID = "T123"
    const val NOT_CONTAINS_NUMBER_PASSWD = "asdasdadasd@@@@#"
    const val NOT_CONTAINS_CHARACTER_PASSWD = "123456123@@@#"
    const val NOT_CONTAINS_SPECIAL_CHARACTER_PASSWD = "123456123asdasd"
    const val WITHIN_8_CHARACTERS_PASSWD = "1234a@b"
}
```
테스트 코드가 다음과 같이 매우 깔끔해 졌음을 볼 수 있다.
```
@Test
fun `아이디와_비밀번호가_모두_형식에_맞다면_로그인버튼이_활성화된다`() {
    composeTestRule.onNodeWithTag(testTag = "ID_TEXT_FIELD")
        .performTextInput(VERIFIED_ID)
    composeTestRule.onNodeWithTag(testTag = "PASSWD_TEXT_FIELD")
        .performTextInput(VERIFIED_PASSWD)
    composeTestRule.onNodeWithText("로그인").assertIsEnabled()
}
```


이제 뷰에 디자인을 입히고 다음 테스트를 작성하러 떠나보자. 👍


## 참고자료

[Compose의 시맨틱 - Android Developer](https://developer.android.com/jetpack/compose/semantics?hl=ko)

[Compose - UI Test by Choi Sang Rok](https://velog.io/@evergreen_tree/Compose-UI-Test)