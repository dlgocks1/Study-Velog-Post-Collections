스프링 부트 어플리케이션을 `war` or `jar`로 생성하여 배포할 수 있다는 사실은 많은 개발자가 알고 있습니다. 대부분의 개발자는 `war`옵션을 건너뛰고 실행 가능한 `JAR`파일을 생성합니다. 

이번 장에서는
* 스프링 부트의 실행 가능한 `JAR`를 빌드할 때 다양한 요구사항과 사용 사례를 충족하는 배포 옵션이 무엇이 있는지 알아보겠습니다. 
* 스프링 부트의 다양한 배포 방법을 검토하고 상대적 장점에 대해 알아봅니다.
* 배포 아티팩트를 만드는 방법을 공부하고, 최적의 실행을 위한 옵션을 알아보겠습니다. 


# 목차


## 실행 가능한 JAR

> **JAR 파일 이란??**
자바 프로그램은 컴파일하여 실행가능한 .class 파일을 생성하게 됩니다. 이 파일들을 묶어서 실행할 수 있는 파일로 만들어 놓은 것이 `jar` 파일입니다.
이것을 다른 사람에게 주면 소스 코드 없이 프로그램을 실행시켜 볼 수 있습니다. 또는 라이브러리처럼 다른 사람이 만든 클래스를 이용하고자 할 때도 `jar` 파일을 통해 임포트하여 해당 기능을 사용할 수 있습니다.

스프링 부트는 `JVM`이 설치되어있는 환경이면 실행이 가능합니다. 

스프링 부트는 앱 플랫폼에서 유지, 관리하는 외부 구성 요소에 대한 의존성을 관리해주며(서블릿 엔진, 데이터베이스, 메시징 라이브러리 등등) 의존성을 변경할 때 생기는 두려움을 줄여줍니다.

스프링 부트 어플리케이션을 활용하면, 핵심 스프링 라이브러리나 여러 계층의 의존성 여부에 관계없이 어떤 의존성이든 업그레이드가 훨씬 덜 고통스럽고, 스트레스도 덜 받습니다.

스프링 부트의 `JAR`에는 스프링 부트 메이븐과 그레이들 플러그인 덕분에 또 다른 유용한 기능이 있습니다. 바로 완전히 실행 가능한 `JAR`을 생성하는 기능입니다. 


### 완전히 실행 가능한 `JAR` 빌드

스프링 부트의 JAR은 외부 다운스트림 의존성이 필요 없는 완전한 어플리케이션으로 구성됩니다.
실행에 필요한 것은 설치된 `JDK`에서 제공하는 `JVM`뿐입니다.

이러한 `JAR`을 생성하기 위해서는
* CLI에서 `gradlew build`를 활용할 수도 있으며
* IDE내부에서 `bootJar`을 활용할 수도 있습니다.![](https://velog.velcdn.com/images/cksgodl/post/304d193d-2fce-410a-9e73-492606b5dc54/image.png)


## JAR 확장

> 스프링 부트의 실행 가능한 `jar`은 `Jar`내에 `jar`를 중첩시키는 접근 방식입니다.

`Jar`내에 있는 종속 `jar`가 손상이나 변경되지 않은 경우, 추출 같은 후속 작업하기에 제격입니다. 실행 가능 `JAR`파일을 추가하는 프로세스를 반대로 하면, 구성 요소 아티팩트가 변경되지 않은 원래 상태로 생성됩니다.

일반적으로 중첩된 `JAR`를 추출하는 명령어는 다음과 같습니다.

`jar -xvf <spring_boot_jar>`

를 실행하게 된다면 `jar`내부의 파일을 추출가능하게 됩니다.

```kotlin
// zipfile /../build/libs/sample1-0.0.1-SNAPSHOT.jar

META-INF/
META-INF/MANIFEST.MF
org/
org/springframework/
org/springframework/boot/
org/springframework/boot/loader/
org/springframework/boot/loader/ClassPathIndexFile.class
org/springframework/boot/loader/ExecutableArchiveLauncher.class
org/springframework/boot/loader/JarLauncher.class
org/springframework/boot/loader/LaunchedURLClassLoader$DefinePackageCallType.class

...

BOOT-INF/lib/netty-codec-socks-4.1.94.Final.jar
BOOT-INF/lib/netty-codec-4.1.94.Final.jar
BOOT-INF/lib/netty-transport-classes-epoll-4.1.94.Final.jar
BOOT-INF/lib/netty-transport-native-unix-common-4.1.94.Final.jar
BOOT-INF/lib/netty-transport-4.1.94.Final.jar
BOOT-INF/lib/netty-buffer-4.1.94.Final.jar
BOOT-INF/lib/netty-resolver-4.1.94.Final.jar
BOOT-INF/lib/netty-common-4.1.94.Final.jar
BOOT-INF/lib/jgrapht-core-1.4.0.jar
BOOT-INF/lib/jheaps-0.11.jar
BOOT-INF/lib/spring-boot-jarmode-layertools-3.1.2.jar
BOOT-INF/classpath.idx
BOOT-INF/layers.idx
```

어플리케이션에 종속되어 있는 수많은 의존성을 확인할 수 있습니다.

이렇게 완전히 실행가능한 `JAR`를 이용하는 방식이 아니라 
`JarLauncher`를 활용해 실행 전반에 걸쳐 일관된 클래스로 로딩 순서를 유지하는 방식이 있습니다.
-> 	하지만 이는 완전히 실행 가능한 `JAR`의 장점을 능가하지 못하빈다. _잘 안쓴다는 뜻_


## 11.3 컨테이너에 스프링 부트 어플리케이션 배포하기

많은 회사가 클라우드 플팻폼을 활용해 어플리케이션을 배포하고 사용합니다.

> 스프링 부트는 그레이들 플러그인 내 도커, 쿠버네티스 등의 주요 컨테이너 엔진/메커니즘이 준수하는 `컨테이너에 대한 기술 표준화(OCI)` 이미지를 생성하는 기능을 제공합니다.

스프링 부트 어플리케이션을 위한 컨테이너 이미지를 직접 만들 수는 있지만 최적의 방법은 아닙니다. 

컨테이너 이미지를 직접 생성하는 것은 어플리케이션 자체의 가치는 더 나아지지 않고 그대로이면서, 일반적으로 프로덕션 버전으로 가기 위한 필요악으로 간주돼어왔습니다.

### 11.3.1 IDE에서 컨테이너 이미지 생성하기

#### 1. `IDE`를 활용하여 이미지 생성하기


스프링 부트 어플리케이션내에서 계층화된 컨테이너 이미지는 `IDE`를 활용하여 쉽게 만들 수 있습니다.

> 이미지를 생성하고자 한다면 로컬 환경에서 도커가 실행 중이어야 합니다.

![](https://velog.velcdn.com/images/cksgodl/post/9b12d3ee-8d99-4cd9-8507-2f5ad20b87c7/image.png)

Gradle 빌드 툴이 제공해주는 docker image 빌드 명령어입니다.

![](https://velog.velcdn.com/images/cksgodl/post/c391d5a0-6f00-4054-90a7-47066c66844a/image.png)


#### 2. `CLI`를 활용하여 이미지 생성하기

도커 컨테이너 설정인 `DockerFile`을 작성합니다. -> 도커파일은 프로젝트 `루트`에 있어야합니다!

```kotlin
FROM amazoncorretto:19
ARG JAR_FILE=build/libs/*.jar
COPY ${JAR_FILE} app.jar
ENTRYPOINT ["java","-jar","/app.jar"]
```

* `FROM amazoncorretto:19`: 이는 도커 이미지를 만들 때 기반이 되는 베이스 이미지를 정의합니다. 

* `ARG JAR_FILE=build/libs/*.jar`: 이는 도커 빌드 시 전달할 변수 JAR_FILE을 정의합니다. 기본적으로 build/libs/*.jar와 같이 지정하여 Spring Boot 프로젝트의 JAR 파일을 선택합니다. 와일드카드를 사용하게 된다면, build/libs/ 디렉토리에 있는 모든 JAR 파일 중 첫 번째 파일을 선택하게 됩니다.

* `COPY ${JAR_FILE} app.jar`: 이 명령은 호스트 머신의 JAR_FILE 경로에 있는 JAR 파일을 도커 이미지의 /app.jar 경로로 복사합니다. 이를 통해 빌드된 Spring Boot JAR 파일을 도커 이미지 내부로 가져옵니다.

* `ENTRYPOINT ["java","-jar","/app.jar"]`: 이는 도커 컨테이너가 실행될 때 실행될 기본 명령을 정의합니다. 여기서는 java -jar /app.jar 명령을 실행하여 Spring Boot 애플리케이션을 실행하게 됩니다. java -jar는 JAR 파일을 실행하는 명령이며, /app.jar는 앞서 복사한 Spring Boot JAR 파일의 경로를 나타냅니다.

---

도커 파일 설정이 끝났으면

스프링 부트 프로젝트의 `루트`에서 다음과 같은 명령어를 통해 `jar`을 생성합니다.

```kotlin
./gradlew wrap
./gradlew build
```
![](https://velog.velcdn.com/images/cksgodl/post/c28dba92-2c79-4b88-a1d0-55b7d4cfb3fa/image.png)


```
BUILD SUCCESSFUL in 4s
```

다음과 같은 명령어가 뜨면 `프로젝트위치/build/libs`에 `jar`이 생성 됩니다.

![](https://velog.velcdn.com/images/cksgodl/post/97f22943-439a-4b1a-a62f-f39a6fac3791/image.png)

이후 해당 파일을 도커로 빌드합니다.

```Dokcer
docker build -t build/libs/sample1-0.0.2.jar .
```

![](https://velog.velcdn.com/images/cksgodl/post/cc58aa00-4639-40cd-9914-bc8a11949463/image.png)

이후 `Docker Images`를 실행하면 이미지가 무사히 추가됨을 볼 수 있습니다.

```kotlin
% docker images           

REPOSITORY                                  TAG        IMAGE ID       CREATED          SIZE
build/libs/sample1-0.0.2.jar                latest     447e61e52834   47 seconds ago   592MB
```

Docker 데스크탑에서도 보이는 것을 확인할 수 있습니다.

![](https://velog.velcdn.com/images/cksgodl/post/4e66c69a-b64c-4aad-bd3c-0de340b84293/image.png)

해당 이미지를 도커에서 `run`하면 도커환경에서 스프링 프로젝트를 돌릴 수 있습니다.

```kotlin
% docker run -p 8080:8080 build/libs/sample1-0.0.2.jar 



  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v3.1.2)

2023-08-07T00:44:57.412Z  INFO 1 --- [           main] .s.d.r.c.RepositoryConfigurationDelegate : Multiple Spring Data modules found, entering strict repository configuration mode ...
```

![](https://velog.velcdn.com/images/cksgodl/post/0894b69d-e4ba-4181-b4ba-28747aa48fec/image.png)

---

### 추가 내용

도커이미지는 `/var/lib/docker`내부에 저장된다고 하지만 맥에서는 약간 다릅니다.

맥은 도커 구동시에 리눅스와는 다르게 바로 도커가 실행되는 구조가 아닙니다.
linux 가상 머신이 생성되고, 가상머신 안에서 도커가 구동되기 때문입니다. `/var/lib/docker`에 접근 하려면 리눅스 가상머신에 접속한뒤에 접근해야합니다.

`Docker Desktop`이나 `docker images` CLI를 이용하면 이미지들을 확인 가능합니다.

![](https://velog.velcdn.com/images/cksgodl/post/36fa88bb-6339-4309-a354-ac5ad7d255ad/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/fe9ea32e-844b-4cf9-b6de-2b670d27a43c/image.png)

## docker hub에 푸쉬하기

`Docker Hub`는 `Docker Repository`를 관리하고 다른 사용자들과 Docker 이미지를 공유하는데 사용됩니다. 

따라서 `Docker Repository`에 이미지를 푸쉬해야 합니다.


1. `Docker Hub`에서 레포지토리 만들기

![](https://velog.velcdn.com/images/cksgodl/post/9ce8477a-6b12-42be-85b0-299e2530ca17/image.png)

웹사이트에서 간단히 만드는 것을 지원함으로 `haechan_docker`라는 이름으로 도커를 생성해 주었습니다.

![](https://velog.velcdn.com/images/cksgodl/post/3bc82be0-86ac-45d8-ad04-d523bdafec7e/image.png)

우측의 `Docker Command`를 확인하면 도커허브에 이미지를 올릴 수 있는 커맨드 예제를 제공합니다.

이미지 이름의 형식은 다음과 같으며 

```
docker push haechan0608/haechan_docker:tagname
docker push <이미지 이름>
```

_이미지 이름을 해당 형식으로 바꾸어 주어야지 이미지가 푸쉬됩니다._


2. 도커 로그인하기

```
docker login
```

로그인을 수행하지 않으면 푸쉬가 안됩니다. :(

3. 이미지 이름 바꾸기

```
// 도커 이미지 체크
docker images 

// 이미지 이름을 위와 같은 형식으로 바꾸기
docker tag <과거 이미지 이름> haechan0608/haechan_docker:first-image       
```

이후 푸쉬를 진행합니다.

```kotlin
% docker push haechan0608/haechan_docker:first-image

The push refers to repository [docker.io/haechan0608/haechan_docker]
0aa59a1009e6: Pushed 
dcd793225fd0: Pushed 
c72ba2be4f59: Pushed 
```

무사히 푸쉬가 진행됨을 볼 수 있습니다.

![](https://velog.velcdn.com/images/cksgodl/post/c63835b5-ffcb-4afb-afae-60f96f0ba963/image.png)

4. 이미지 Pull 받기

이후 해당 이미지를 로컬에서 삭제하고 다시 풀받아 보겠습니다.

이미지 파일을 로컬에서 모두 지워줍니다.

```kotlin
% docker images
REPOSITORY                                  TAG        IMAGE ID       CREATED             SIZE
docker/welcome-to-docker                    latest     605de626b242   6 weeks ago         13.9MB
hello-world                                 latest     b038788ddb22   3 months ago        9.14kB
```

이후 도커 이미지를 풀 받아 줍니다.

```kotlin
% docker pull haechan0608/haechan_docker:first-image

first-image: Pulling from haechan0608/haechan_docker
Digest: -00000-
Status: Downloaded newer image for haechan0608/haechan_docker:first-image
docker.io/haechan0608/haechan_docker:first-image
```

이후 해당 이미지를 확인할 수 있습니다.

![](https://velog.velcdn.com/images/cksgodl/post/91188b8b-9372-4553-a7ad-0928c296b141/image.png)

![](https://velog.velcdn.com/images/cksgodl/post/b5dce4ca-ee1b-43a1-a6e4-57edaad8eea1/image.png)

이제 해당 이미지를 실행합니다.

```
% docker run -p 8080:8080 haechan0608/haechan_docker:first-image

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v3.1.2)

// ....
```

![](https://velog.velcdn.com/images/cksgodl/post/f7dfd279-df8c-4369-913d-f6af1897369f/image.png)

이렇게 로컬 환경에서 이미지를 풀받아 컨테이너를 뛰우고 실행해 보았습니다.

