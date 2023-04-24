![](https://velog.velcdn.com/images/cksgodl/post/551ff13c-a1cd-49e3-b91f-57e67e8a960e/image.gif)

## Firebase Realtime Database 란??

> `Firebase Realtime Database`는 Google에서 제공하는 NoSQL기반 데이터베이스 서비스이다.
> 이 서비스를 사용하면 클라우드에 데이터를 저장하고 실시간으로 동기화 할 수 있다.
> 빠르고 안정적이며 확장성이 뛰어나므로 대규모 애플리케이션에서도 사용할 수 있다.

이런 동기화를 통해 모바일 앱이나 웹 애플리케이션에서 데이터를 쉽게 공유하고 업데이트할 수 있도록 도와준다.

데이터는 `JSON` 형식으로 저장되며, `Firebase SDK`를 사용하여 앱 및 웹에서 쉽게 데이터를 읽고 쓸 수 있다.

## 1. Firebase Project 등록 및 RealTime Database 사용 설정하기

[파이어 베이스](https://console.firebase.google.com/)에서 튜토리얼을 너무 잘 제공해주고 있지만 간단하게 몇 가지 더 적어 보겠다. \__230331 Ver_

#### 초기 프로젝트를 만든 후

### 앱등록

![](https://velog.velcdn.com/images/cksgodl/post/0e0bc9e5-06f8-4b61-a704-795bf206c0f0/image.png)

- SHA-1 키는 gradle signingReport를 활용하여 획득할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/fc387a36-e2c2-4b83-9113-ddc6def762e9/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/0fab948b-32aa-42d6-beda-7396047e81d5/image.png)

### google-services.json 넣기

`./projectName/app/`경로에 넣으면 된다.

### Firebase SDK 추가

`루트 수준(프로젝트 수준) Gradle파일`의 형식이 약간 바뀐 점을 주의

```
// Gradle - project
buildscript {
    dependencies {
        classpath 'com.google.gms:google-services:4.3.15'
    }
}
plugins {
    // ...
}


// Gralde - Module
plugins {
	// ..
    id 'com.google.gms.google-services'
}

dependencies {

    // Firebase Realtime Database
    implementation 'com.google.gms:google-services:4.3.15'
    implementation 'com.google.firebase:firebase-database:20.1.0'
    implementation platform('com.google.firebase:firebase-bom:31.3.0')
}
```

### 2. Realtime Database 사용 설정

테스트용으로 만들것이기 때문에 `read`권한과 `write`권한을 임시로 모두 풀어준다.

![](https://velog.velcdn.com/images/cksgodl/post/cf4329e2-82ab-40a5-bdfe-439fe250fa0c/image.png)

```
{
  "rules": {
    ".read": "now < 1682780400000",  // 2023-4-30
    ".write": "now < 1682780400000",  // 2023-4-30
  }
}
```

### 3. Firebase SDK에서 실시간 데이터베이스 인스턴스 가져오기

일단 간단하게 채팅을 볼 뷰를 작성하고
![](https://velog.velcdn.com/images/cksgodl/post/a8d75418-92c6-424b-87ff-f15226dc32c9/image.png)

`Firebase Realtime Database` 인스턴스를 가져와준다.

```
private lateinit var databaseReference: DatabaseReference

override fun onCreate(savedInstanceState: Bundle?) {
	super.onCreate(savedInstanceState)

	// Firebase Realtime Database 초기화
	val firebaseDatabase: FirebaseDatabase = FirebaseDatabase.getInstance()
	databaseReference = firebaseDatabase.getReference("Chat")
}
```

실시간 데이터베이스의 `getReference`를 `Chat`으로 가져오고 있기에 실제 데이터베이는 다음과 같이 만들어진다.

![](https://velog.velcdn.com/images/cksgodl/post/7eb4610f-c704-45a2-aec9-9ff0e1105fb1/image.png)

---

이제 데이터베이스에 전달할 `ChatMessage` 자료구조를 간단하게 만들고

```
data class ChatMessage(
    val message: String? = "메시지 오류",
    val name: String? = "이름 오류",
    val uploadDate: String? = ""
)
```

실제 데이터베이스가 `Update`될 때 마다 뷰를 업데이트해 줘야하기 때문에 이벤트 리스너를 달아 뷰를 업데이트 해준다.

```
// Firebase Realtime Database에서 채팅 메시지 읽기
databaseReference.addChildEventListener(object : ChildEventListener {

	// 새로운 자식이 추가 됬을 때
	override fun onChildAdded(dataSnapshot: DataSnapshot, s: String?) {
        val chatMessage: ChatMessage =
            dataSnapshot.getValue(ChatMessage::class.java) ?: return
        chatList.add(chatMessage)
        chatRvAdapter.submitList(chatList)
        chatRvAdapter.notifyDataSetChanged()
        binding.chatRv.smoothScrollToPosition(chatRvAdapter.itemCount - 1)
    }

    override fun onChildChanged(dataSnapshot: DataSnapshot, s: String?) {}
    override fun onChildRemoved(dataSnapshot: DataSnapshot) {}
    override fun onChildMoved(dataSnapshot: DataSnapshot, s: String?) {}
    override fun onCancelled(databaseError: DatabaseError) {}
})
```

여기서 `DataSnapshot.getValue()`는 다음과 같이 구현되어 있으며 커스텀클래스로의 타입캐스트를 지원한다. (따라서 `ChatMessage`의 모든 속성을 `nullable`로 지정)

```
  @Nullable
  public <T> T getValue(@NonNull Class<T> valueType) {
    Object value = node.getNode().getValue();
    return CustomClassMapper.convertToCustomClass(value, valueType);
  }
```

새로운 메시지를 보내기 위해서는 다음과 같이 `sendMessage()`를 작성할 수 있다.

```
private fun sendMessage() {
    val userChat = binding.chatEt.text
    if (userChat.isNotBlank()) {
        val chatMessage = ChatMessage(
            message = userChat.toString().trim(),
            name = nickName,
            uploadDate = LocalDateTime.now().toString()
        )
        databaseReference.push().setValue(chatMessage)
        binding.chatEt.setText("")
    }
}
```

![](https://velog.velcdn.com/images/cksgodl/post/06ed688c-4a35-402d-ad3f-8f9dc8e93c47/image.gif)

해당 채팅들은 실시간 데이터베이스에 다음과 같이 남게된다.

![](https://velog.velcdn.com/images/cksgodl/post/7a989f74-b381-4446-9ea3-87dc95e4aced/image.png)

---

> 이렇게 간단하게 Firebase Realtime Database를 활용하여 익명 채팅 앱을 만들어 보았다.
