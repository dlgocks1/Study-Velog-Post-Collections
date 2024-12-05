## Problem

로그인, 회원가입을 구현하며 아래의 사진과 같이 마지막 자리만 보이는 텍스트 필드를 활용해 비밀번호 입력을 받고자 한다.

![](https://velog.velcdn.com/images/cksgodl/post/f49e8d0e-4320-4c64-9280-d553a1d69163/image.png)


## Solution

여러 텍스트 필드 컴포저블 중 `BasicTextField`를 활용하였다.

```
Basic composable that enables users to edit text via hardware or software keyboard, 
but provides no decorations like hint or placeholder.

하드웨어 또는 소프트웨어 키보드를 통해 텍스트를 편집할 수 있지만
힌트나 자리 표시자와 같은 장식은 제공하지 않는 기본 컴포저블
```

`BasicTextField`에서 제공하는 속성인 `visualTransformation`를 활용하여 이를 구현할 수 있었다.

```
visualTransformation
The visual transformation filter for changing the visual representation of the input. 
By default no visual transformation is applied.

텍스트 입력 시 보이는 시각적 표현을 변경하기 위한 시각적 변환 필터입니다.
시각적 변형은 실제 텍스트에 적용되지 않습니다.
```

`visualTransformation`속성의 기본 `Default`값은 `VisualTransformation.None`으로 적용되며 이는 텍스트를 있는 그대로 노출한다.

컴포즈에서는 `PasswordVisualTransformation()`도 제공하며 해당 값을 적용하면 `*`를 활용해 텍스트를 표시해준다. 
```
VisualTransformation.None -> 1234G
PasswordVisualTransformation() -> *****
```

---


해당 `PasswordVisualTransformation`을 커스텀하여 마지막 자리수만 보이는 텍스트 필드로 만들 것이다.

```
class PasswordVisualTransformation(val mask: Char = '\u2022') : VisualTransformation {
    override fun filter(text: AnnotatedString): TransformedText {
        return TransformedText(
            AnnotatedString(mask.toString().repeat(text.text.length)),
            OffsetMapping.Identity
        )
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is PasswordVisualTransformation) return false
        if (mask != other.mask) return false
        return true
    }

    override fun hashCode(): Int {
        return mask.hashCode()
    }
}
```

`AnnotatedString(mask.toString().repeat(text.text.length))`부분에서 해당 텍스트의 크기만큼 `*`으로 바꾸어 텍스트를 반환하는 것을 볼 수 있다. 해당 부분을 바꾸어 마지막 자리가 보이는 텍스트필드를 커스텀해 보자.

```
 override fun filter(text: AnnotatedString): TransformedText {
        return TransformedText(
            text = if (text.text.isNotEmpty()) {
                    AnnotatedString(mask.toString().repeat(text.text.length - 1) + text.text.last())
                } else {
                    AnnotatedString(mask.toString().repeat(text.text.length))
                },
            offsetMapping = OffsetMapping.Identity
        )
    }
```

다음과 같이 소스를 작성하면 간단하게 마지막 자리수가 보이는 텍스트 필드를 만들 수 있다.

### Problem #1

![](https://velog.velcdn.com/images/cksgodl/post/03ae7441-3233-449e-8586-ed42435904b8/image.png)

마지막 글자가 보이기는 하지만, 해당 텍스트필드에 포커스가 존재하지 않아도 마지막 글자가 계속 보인다. 

> 해당 텍스트필드에 포커스가 있을 때만 마지막 자리수가 보이도록

수정해보자.

```
class LastPasswordVisibleVisuualTransformation(
    private val mask: Char = '\u2022',
    private val isFocused: Boolean,
) : VisualTransformation {
    override fun filter(text: AnnotatedString): TransformedText {
        return TransformedText(
            text = if (isFocused) {
                if (text.text.isNotEmpty()) {
                    AnnotatedString(mask.toString().repeat(text.text.length - 1) + text.text.last())
                } else {
                    AnnotatedString(mask.toString().repeat(text.text.length))
                }
            } else {
                AnnotatedString(mask.toString().repeat(text.text.length))
            },
            offsetMapping = OffsetMapping.Identity
        )
    }
}
```

`LastPasswordVisibleVisuualTransformation`내에서는 포커스에 대한 정보를 얻을 수 없다. 포커스에 대한 정보를 부모에게서 받아와 이를 적용해야 한다.

```
val hasFocus = remember {
    mutableStateOf(false)
}

BasicTextField(
    modifier = modifier
        .onFocusChanged {
            hasFocus.value = it.isFocused
        }
    value = value,
    onValueChange = {
        if (it.length <= 25) onvalueChanged(it)
    },
    visualTransformation = LastPasswordVisibleVisuualTransformation(isFocused = hasFocus.value)
    
)
```

커스텀 컴포저블 외부에 `hasFocus` 상태를 정의하고 이를 자식에게 보내 포커스가 적용 안될 때 마지막 글자를 가리는 것에 성공했다.


### Problem #2 

![](https://velog.velcdn.com/images/cksgodl/post/3e62bc5d-f735-4e0f-bebd-0adeff8d904c/image.png)

해당 아이콘이 눌렸을 때는 전체 비밀번호가 보여야 하며, 다시 눌렀을 때는 마지막 비밀번호만 보여야 한다.

```
val pswdVisible = remember {
	mutableStateOf(false)
}

// ...

visualTransformation = if (pswdVisible.value) VisualTransformation.None else {
    LastPasswordVisibleVisuualTransformation(isFocused = hasFocus.value)
}
```

패스워드 아이콘에 대한 상태를 선언하여 해당 상태일 때에 따라 `visualTransformation` 을 변화시켜 커스텀한다. 


## 전체 소스

그외에도 `keyboardOptions`, `keyboardActions`, `placeholder`, `focusRequest` 등의 속성을 추가하여 `BasicTextField`를 감싸는 커스텀 텍스트 필드를 만들 수 있다.

```
/**
 * 마지막 자리 비밀번호가 보이는 비밀번호 용 커스텀 텍스트 필드
 */
@Composable
fun LastPasswordVisibleCustomTextField(
    modifier: Modifier = Modifier,
    leadingIcon: @Composable() (() -> Unit)? = {},
    placeholderText: String = "",
    fontSize: TextUnit = 16.sp,
    focusRequest: FocusRequester? = null,
    keyboardOptions: KeyboardOptions? = null,
    keyboardActions: KeyboardActions? = null,
    value: String,
    onvalueChanged: (String) -> Unit,
    onErrorState: Boolean = false,
) {
    val hasFocus = remember {
        mutableStateOf(false)
    }
    val pswdVisible = remember {
        mutableStateOf(false)
    }
    val bottomLineColor = remember {
        mutableStateOf(Gray600)
    }

    BasicTextField(
        modifier = modifier
            .focusRequester(focusRequest ?: FocusRequester())
            .onFocusChanged {
                hasFocus.value = it.isFocused
                if (it.isFocused) {
                    bottomLineColor.value = Color.Black
                } else {
                    bottomLineColor.value = Gray600
                }
            }
            .bottomBorder(1.dp, if (onErrorState) Error_Color else bottomLineColor.value),
        value = value,
        onValueChange = {
            if (it.length <= 25) onvalueChanged(it)
        },
        singleLine = true,
        cursorBrush = SolidColor(MaterialTheme.colorScheme.primary),
        textStyle = LocalTextStyle.current.copy(
            color = Color.Black,
            fontSize = fontSize,
        ),
        keyboardOptions = keyboardOptions ?: KeyboardOptions(),
        keyboardActions = keyboardActions ?: KeyboardActions(),
        decorationBox = { innerTextField ->
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.padding(0.dp, 15.dp)
            ) {
                if (leadingIcon != null) leadingIcon()
                Box(Modifier.weight(1f)) {
                    if (value.isEmpty()) {
                        Text(
                            placeholderText,
                            style = LocalTextStyle.current.copy(
                                color = Color.Black.copy(alpha = 0.3f),
                                fontSize = fontSize,
                            ),
                        )
                    }
                    innerTextField()
                }
                if (pswdVisible.value) {
                    Icon(
                        painter = painterResource(id = com.cmc12th.runway.R.drawable.ic_able_pw),
                        tint = Gray600,
                        contentDescription = "IC_ABLE_PW",
                        modifier = Modifier
                            .size(24.dp)
                            .clickable {
                                pswdVisible.value = !pswdVisible.value
                            },
                    )
                } else {
                    Icon(
                        painter = painterResource(id = com.cmc12th.runway.R.drawable.ic_disable_pw),
                        tint = Color.Unspecified,
                        contentDescription = "IC_DISABLE_PW",
                        modifier = Modifier
                            .size(24.dp)
                            .clickable {
                                pswdVisible.value = !pswdVisible.value
                            },
                    )
                }
            }
        },
        visualTransformation = if (pswdVisible.value) VisualTransformation.None else {
            LastPasswordVisibleVisuualTransformation(isFocused = hasFocus.value)
        }
    )
}
```

