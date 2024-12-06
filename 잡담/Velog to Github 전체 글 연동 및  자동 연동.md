### [velog migration scripts - Github](https://github.com/dlgocks1/velog_migration_scripts)

# 배경

회사를 다니며 깃허브 프로필의 잔디가 점점 사라져 사막화가 진행되고 있는 상황

- 취업 전 (7월 이전) 

![](https://velog.velcdn.com/images/cksgodl/post/13ce14ec-05cd-418b-a884-fb4ee904d37b/image.png)

- 취업 전 (24년)

![](https://velog.velcdn.com/images/cksgodl/post/2184e0be-d924-4246-9a77-443efe922948/image.png)

블로그에 글은 자주 올렸지만 잔디는 텅텅 비어서, `velog`에 글을 쓰면 잔디가 채워지는 것이 있으면 좋겠다 생각하여 만들게 되었습니다.


## 레퍼런스

아래 내용은 [velog 글 작성 시, 자동으로 github에 커밋하기](https://velog.io/@rimgosu/velog-%EA%B8%80-%EC%9E%91%EC%84%B1-%EC%8B%9C-%EC%9E%90%EB%8F%99%EC%9C%BC%EB%A1%9C-github%EC%97%90-%EC%BB%A4%EB%B0%8B%ED%95%98%EA%B8%B0)를 기반으로 작성되었습니다.

### 차이점

#### 시리즈별 정리

![](https://velog.velcdn.com/images/cksgodl/post/abbee025-682a-4cc0-b0f8-a0f89b2e20c8/image.png) 위 블로그의 예시는 사진처럼 정돈되지 않게 작성되기에 약간 수정하여 아래 사진처럼 시리즈별로 정돈되어 폴더링되도록 변경하였습니다.

![](https://velog.velcdn.com/images/cksgodl/post/6b48c877-4ed6-45ba-ab4a-8616cc94fb37/image.png)

#### 전체 글 배치

매일 글을 `Github`에 연동할 뿐만 아니라, `velog`에 작성하였던 모든 글을 `Github`에 연동하는 기능을 추가했습니다.

#### 본인 잔디 심기

본인 `Github` 토큰 및 아이디를 활용하여 자동으로 잔디가 심어지도록 수정하였습니다.

![](https://velog.velcdn.com/images/cksgodl/post/db296ef9-8063-490d-8470-a6e54691d934/image.png)

_일괄 배치 시 필자는 316개의 커밋이 생성_


# Velog to Github Migration

> `Velog`작성 글을 `Series`기반으로 Github와 연동하는 프로젝트 입니다.
>
> 적용 [Sample](https://github.com/dlgocks1/Study-Velog-Post-Collections) 예제


## 세팅

1. 본인의 레포지토리를 생성하고 [velog migration scripts - Github](https://github.com/dlgocks1/velog_migration_scripts)의 내용을 모두 붙여넣거나, 해당 레포지토리를 클론합니다.

2. 프로젝트 내부의 `<<Github ID>>`, `<<Github Email>>`, `<<Velog ID>>`, `<<Current Repository Name>>`을 찾아서 변경합니다.
![](https://velog.velcdn.com/images/cksgodl/post/b1d9af79-3554-47c1-8589-3d362484459e/image.png)
   - Current Repository는 본인 레포지토리 주소를 의미합니다.


3. `Github PAT`를 발급받아 `Github Seceret`에 등록합니다.

    - [Github Personal Access Token 발급 방법](https://velog.io/@hjthgus777/Github-Personal-Access-Token-%EB%B0%9C%EA%B8%89)
    - 레포지토리 `Settings` -> `Secretes and variants` -> `Repository secrets`
      ![](https://velog.velcdn.com/images/cksgodl/post/c08d5fc8-abb3-440e-881d-9bbc0497d315/image.png)
    - Name : `GH_PAT`, Secret : `<발급받은 토큰>`

---

## 설명

위 프로젝트는 아래의 2가지 `Github Action`으로 이루어 집니다.

### `Upload all velog posts by series`

`Velog`의 모든 글을 시리즈기반으로 깃허브와 연동하는 `Github Action` 스크립트입니다.
- 시리즈 정보를 활용해 폴더링 합니다.
- 중복이면 덮어 쒸워지도록 진행됩니다.

#### 실행 법

1. `Actions` -> `Upload all velog posts by series` -> `Run workFlow`를 진행합니다.
  ![](https://velog.velcdn.com/images/cksgodl/post/e399c03b-aa24-437a-8ddf-7553cbf4fec7/image.png)


2. 레포지토리에 업로드 완료 되었는지 확인합니다.
   ![](https://velog.velcdn.com/images/cksgodl/post/61bb8f10-1aad-4318-bb04-2ef2a6e0775e/image.png)


### `Upload daily velog posts`

매일 새벽 2시에 블로그의 N개(기본 10개)를 쿼리하여 작성되어있지 않은 글이면 작성하는 `Github Action Cron` 입니다.
- 만약 작성한 글에 시리즈가 없다면 무시
- 시리즈 정보를 가져와서 폴더링
   - 이미 존재하면 무시 (제목을 기준으로 필터링합니다. 제목이 바뀔 시 중복 저장 가능)

#### 실행 법

1. 세팅을 완료하면 크론이 자동 실행됩니다. (기본 새벽 2시 실행)
2. 레포지토리에 업로드 완료 되었는지 확인합니다.
   ![](https://velog.velcdn.com/images/cksgodl/post/53ddc50b-dc9b-4eb5-be16-52dbc76b9d0a/image.png)

### 적용 예제

- [Study-Velog-Post-Collections](https://github.com/dlgocks1/Study-Velog-Post-Collections)



