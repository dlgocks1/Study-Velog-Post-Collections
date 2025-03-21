# 1장 쿠버네티스 소개

`MSA`환경으로 나아가면서 개별 배포, 업데이트, 확장을 제공해주는 쿠버네티스가 등장하게 되었다.

쿠버네티스는 어플리케이션 개발과 운영을 분리하여 개발자가 운영 팀의 도움 없이도 어플리케이션 배포를 할 수 있도록 한다.

> k8s라 불리는 이유는 kubernetes에서 "k"와 "s"사이에 8글자가 들어가있기 때문이다.

## 쿠버네티스의 등장 배경

책의 내용은 모두 [Kuberneteses.io](https://kubernetes.io/docs/concepts/overview/)의 내용을 기반으로 만들어졌다. 이를참고하는게 더 정확

최근 몇넌 동안의 어플리케이션 개발과 배포방식은 많이 변화 했다.

![](https://velog.velcdn.com/images/cksgodl/post/96eaca95-39b1-481b-8384-88ddc153bb0e/image.png)


#### 모놀리스 어플리케이션에서 마이크로서비스로의 전환

모놀리스 어플리케이션은 하나의 OS에서 여러 프로세스로 실행되기 떄문에 대부분 하나의 개체로 개발, 배포 및 관리되어야 했다. 이에 따라 시스템의 복잡성이 증가하게 되었다.

또한 수평확장 시 어플리케이션에 대한 복제가 필요하며, 업데이트시에는 모든 어플리케이션을 수동으로 재시작해야 했다.

(어플리케이션 일부를 수평적으로 확장하도록 구조를 수정하는 것도 힘듦)

#### 마이크로서비스로 어플리케이션 분할

![](https://velog.velcdn.com/images/cksgodl/post/5c3d1a7d-1ded-4215-8662-4a26cd0fc332/image.png)

모놀리스 어플리케이션과 달리 마이크로서비스는 각각의 서비스가 분리되어 실행시키에 확장과 복제, 수정이 용이하다. 또한 수평 확장이 불가능할 경우에도 수직확장도 용이하다.

> 쿠버네티스 환경 위에서는 노드와 포드 그 위의 컨테이너를 활용하여 수평적으로 확장을 진행한다.

#### 마이크로서비스 배포

구성 요소가 많아지면 배포 조합의 수뿐만 아니라 구성 요소 간의 상호 종속성 수가 훨씬 많아짐으로 배포 관련 결정이 어려워진다.

마이크로서비스는 여러 개가 서로 함께 작업을 수행함으로 서로를 찾아 통신한다. 전체가 하나의 시스템처럼 동작할 수 있는 프레임워크가 필요하게 됬으며 쿠버네티스가 등장하게 되었다.

> 마이크로 서비스간의 통신에 대한 추적은 `PinPoin`, `Zipkin`과 같은 분산추적 시슽메을 통해 해결해야 한다.


#### 환경 요구 사항의 다양성

모놀리스 어플리케이션에서는 하나의 어플리케이션이 다양한 일을 수행하고, 다양한 일들이 필요한 라이브러리에 대한 종속성 관리가 매우 복잡하다. 

`MSA`환경에서는 각각의 서비스가 서로 다른 종속성, 심지어는 다른 프레임워크 위에서 동작하여 각각의 서비스를 개별적으로 관리하기 편리하다.

또한 베타환경과 릴리즈환경에서 동일한 환경으로 개발을 진행할 수 있다. (현재 표준으로 적용된 도커의 콘테이너를 활용한다.)  이에따라 프로덕션에서의네트워킹 환경, 운영체제 환경, 라이브러리 등을 동일하게 구성하여 개발할 수 있다.


#### 데브옵스 - 지속적인 배포

과거에는 개발자가 어플리케이션을 만들고 (`Jar`파일) 이를 운영 팀에게 넘겨주어 운영팀이 관리하였다. 하지만 오늘날, 개발 팀이 어플리케이션을 배포하고 관리하는 것이 더 낫다는 것을 깨달았다. 즉 개발자, 품질 보증, 운영 팀이 전체 프로세스에서 협업한다 이를 데브옵스라고 부른다.

> 개발자가 프로덕션 환경에서 어플리케이션을 실행하면 할수록 버그의 확률이 줄어든다. 따라서 개발자가 운영 담당자를 기다리지 않고 직접 어플리케이션을 배포하는 것이 가장 이상적일 것이다.

하지만 대게의 경우 인프라와 데이터 센터의 하드웨어구성에 대해서 알아야 하며 배포에 따른 사이드이펙트, 적절한 하드웨어 사양또한 알아야한다. 개발자들은 이런 정보를 알지 못하며, 알고 싶어 하지도 않는다.

__따라서 하드웨어 인프라를 전혀 알지 못해서 운영 팀을 거치지 않고 개발자가 어플리케이션을 직접 배포하는 방식이 이상적이며 이것을 노옵스라고 한다.__

쿠버네티스를 활용하면 이 모든 것을 해결할 수 있다.

## 1.2 컨테이너 기술

쿠버네티스는 리눅스의 컨테이너 기술을 활용한다.

### 컨테이너란?

기존 `VM`을 활용해 마이크로서비스 환경을 분리하는 대신 개발자들은 리눅스 컨테이너 기술로 눈을 돌렸다. 이는 동일한 호스트 시스템에서 여러 개의 서비스를 실행할 수 있으며 동시에 서로 다른 환경을 만들어줄 뿐만 아니라 가상머신과 유사하게 서로 격리하지만 오버헤드가 훨씬 적다.

#### 가상머신과의 비교

> 컨테이너는 호스트 OS에서 실행되는 하나의 격리된 프로세스에 지나지 않는다.

따라서 컨테이너는 가상머신에 비해 훨씬 더 가벼워서 동일한 하드웨어에서 더 많은 수의 소프트웨어 구성 요소를 실행할 수 있다.

![](https://velog.velcdn.com/images/cksgodl/post/462a64f2-a1c3-4c37-9664-3478d63fd326/image.png)

__컨테이너는 호스트 OS에서 실행되는 동일한 커널에서 시스템 콜을 수행한다.__ 이 커널은 호스트 CPU에서 x86명령을 수행하는 유일한 커널이다. 즉, CPU는 가상머신과 같은 방식으로 어떠한 종류의 가상화도 필요가 없다.

컨테이너는 가상머신처럼 부팅할필요가 없으며, 컨테이너에서 실행되는 프로세스는 즉시 시작된다.

### 컨테이너 격리는 어떻게 가능한거야?

동일 OS에서의 콘테이너 분리는 두 가지 메커니즘으로 제공된다.

- 리눅스 네임스페이스로 각 프로세스가 시스템(파일, 프로세스, 네트워크 인터페이스, 호스트 이름)에 대한 독립된 뷰만 볼 수 있도록 한다.
- `cgroups`를 통해 사용할 수 있는 리소스의 양을 제한한다.(CPU, 메모리, 네트워크 대역폭)

기본적으로 리눅스 시스템은 초기 구동 시 하나의 네임스페이스가 있다. 프로세스를 실행할 때는 하나의 네임스페이스를 골라 실행하게 된다. (동일한 네임스페이스 내에 있는 리소스만 볼 수 있다.) 여러 종류의 네임스페이스가 있기 떄문에 프로세스는 여러 네임스페이스에 속할 수도 있다.

네임스페이스의 종류는 다음과 같다.

- 마운트
- 프로세스 ID
- 네트워크
- 프로세스 간 통신(IPC)
- 호스트와 도메인 이름
- 사용자 ID

리눅스 커널 기능인 `cgroups`은 프로세스의 리소스 사용량을 제한할 수 있게 해준다. 따라서 프로세스는 다른 프로세스용으로 예약된 리소스를 사용할 수 없으며, 각 프로세스가 별도의 시스템에서 실행될 떄와 비슷하다.

### 도커 컨테이너 플랫폼 소개

어플리케이션뿐만 아니라 라이브러리, 종속성, 운영체제 파일시스템까지도 도커 컨테이너로 묶을 수 있다. 도커는 컨테이너를 여러 쉽게 이식 가능하게 하는 최초의 컨테이너 시스템이다.

> 이는 가상머신에 운영체제를 설치하고 그 안에 어플리케이션을 설치한 다음 가상머신 이미지를 배포하고 실행하는 가상머신 이미지를 만드는 것과 유사하다.

도커는 컨테이너 기술로 가상머신과 거의 동일한 수준의 격리를 제공한다. 

도커 컨테이너 이미지의 큰 차이점은 컨테이너 이미지가 여러 이미지에서 공유되고 재사용될 수 있는 레이어로 구성되어 있다. -> 동일한 레이어를 포함하는 다른 컨테이너 이미지를 실행할 때 다른 레이어가 이미 다운로드된 경우 이미지의 특정 레이어만 다운로드하면 된다.(캐싱 가능)

### 도커 개념 이해

도커는 어플리케이션을 패키징, 배포, 실행하기 위한 플랫폼이다. 어플리케이션을 전체 환경과 함께 패키지화할 수 있다. 이런 도커 이미지는 도커 허브에 저장되어 다양한 곳에서 활용될 수 있다.

- 이미지 : 어플리케이션과 해당 환경을 패키지화한 것이다. 여기에는 어플리케이션에서 사용할 수 있는 파일시스템과 이미지가 실행될 때 실행돼야 하는 실행파일 경로와 같은 메타데이터가 포함돼 있다.

- 레지스트리 : 도커 이미지를 저장하고 공유할 수 있는 저장소이다.

- 컨테이너 : 도커 기반 컨테이너 이미지에서 생성된 일반적인 리눅스 컨테이너이다.

## 쿠버네티스 소개

구글은 사내 내부 시스템인 보그, 오메가를 개발하며 얻은 경험을 기반으로 쿠버네티스를 소개했다.

이는 컨테이너화된 어플리케이션을 쉽게 배포하고, 관리할 수 있게 해주는 소프트웨어 시스템이다. 리눅스 컨테이너의 기능에 의존해 어플리케이션의 내부 세부 사항을 알필요 없이, 각 호스트어플리케이션을 수동으로 배포할 필요도 없이 실행할 수 있다.

- 쿠버네티스는 여러 어플리케이션을 동일한 워커 노드에 배포한다. 
- 쿠버네티스는 서비스 회복, 스케일링, 로드밸런싱, 자가 치유, 리더 선출 등을 제공하기에 개발자는 비즈니스로직에 집중할 수 있다.

### 쿠버네티스 클러스터 아키텍처의 이해

하드웨어 수준에서 쿠버네티스 클러스터는 두 유형의 노드로 나뉜다.

- 마스터 노드 : 쿠버네티스 시스템을 제어하고 관리하는 쿠버네티스 컨트롤 플레인을 의미한다.
- 워커 노드 : 실제 배포되는 컨테이너 어플리케이션을 실행

### 컨트롤 플레인

> 컨트롤 플레인은 클러스터를 제어하고 작동시킨다.

- 컨트롤 플레인(마스터 노드)
  - etcd
  - 스케줄러
  - 컨트롤러 매니저

- 워커 노드
  - kube-proxy
  - kubelet
    - 컨테이너 런타임 

---

- 스케줄러는 어플리케이션의 배포를 담당한다.
- 컨트롤러 매니저는 레플리카, 워커 노드, 노드 장애 처리 등과 같은 클러스터단의 기능을 수행한다.
- `Etcd`는 클러스터 구성을 지속적으로 저장하는 신뢰할 수 있는 분산 데이터 저장소이다. (키 밸류)

### 노드

워커 노드는 컨테이너화된 어플리케이션을 실행하는 시스템이다. 이는 어플리케이션을 실행하고 모니터링하며 어플리케이션에 서비스를 제공하는 작업은 다음 구성 요소에 의해 수행된다.

- 컨테이너를 실행하는 도커
- API 서버와 통신하고 노드의컨테이너를 관리하는 `kubelet`
- 어플리케이션 구성 요소 간의 네트워크 트래픽을 로드밸런싱하는 쿠버네티스 서비스 프록시

## 쿠버네티스에서 어플리케이션 실행

쿠버네티스에서 어플리케이션을 실행하기위한 순서는 다음과 같다.

1. 어플리케이션을 하나 이상의 컨테이너 이미지로 패키징한다.
2. 이미지를 레지스트리로 푸시한다.
3. 쿠버네티스 API 서버에 어플리케이션 디스크립션을 작성한다.

> 책에서는 `디스크립션`이라고 하지만 공식문서에서는 `manifest`, `helm`을 의미하기도 한다.

디스크립션에서는 

- 컨테이너의 이미지 
- 해당 구성 요소가 서로 통신하는 방법
- 동일 서버에 함께 배치돼야 하는 구성요소

이러한 파이프라인을 생성해 실행시키면 쿠버네티스는 가용가능한 노드위에 콘테이너를 설치하게 된다. (포드의 레플리카는 다른 노드에 설치될 수 있다.)

#### 어플리케이션 실행 후 

어플리케이션이 실행되면 쿠버네티스는 어플리케이션의 배포 상태가 사용자가 제공한 디스크립션과 일치하는지 지속적으로 확인한다. (기본값은 5초로 하트비트가 전송 됨)

#### 복제본 수 스케일링

복제본 수를 늘릴지 줄일지 결정할 수 있으며, 쿠버네티스는 추가 복제본을 기동하거나 초과 복제본을 정지할 수 있다. 

이런 스케일리의 조건으로는 `CPU, 메모리 사용량`, `네트워크 트래픽 량`등을 활용할 수 있으며 어플리케이션에서 외부로 노출하는 메트릭을 기반으로 할 수 도 있다.

자세한 내용은 `HPA`에 대해 더 공부해보기

#### 이동하는 컨테이너에 접근하기

포드는 여러 워커 노드에설치도리 수 있으며, 이는 언제든 죽을 수도, 살아날 수도 있다. 그렇다면 이런 분산된 포드와 컨테이너에 어떻게 접근할 수 있을까?

`kube-proxy`는 서비스를 제공하는 모든 컨테이너에서 서비스 연결이 로드밸런싱 되도록 한다. 외부로 노출 되는 IP주소는 일정하며 `DNS`를 통해 제공될 수도 있다.

## 쿠버네티스의 장점

- **어플리케이션 배포의 단순화**

모든 워커 노드를 한아ㅢ 배포 플랫폼으로 제공하기에 개발자가 인프라팀의 도움없이 자체적으로 배포를 시작할 수 있으며 클러스터를 구성하는 서버에 관해 알 필요가 없다.

- **하드웨어 활용도 높이기**

`helm`에 작성한 리소스 기반으로 적절한 노드를 선택하여 포드를 배포한다. 따라서 노드의 하드웨어 리소스를 최대한 활용할 수 있다. 

또한 쿠버네티스는 언제든지 클러스터 간에 어플리케이션이 이동할 수 있으므로, 수동으로 수행하는 것 보다 훨씬 더 인프라를 잘 활용할 수 있다.

- **상태확인과 자가 치유**

포드와 컨테이너 모두 하트비트 및 `livenessProve`, `readienessProve`를 제공하기에 모니터링이 제공되며 이에 따라 `backOff`알고리즘을 활용해 자가 치유가 제공된다.

- **오토스케일링**

`HPA`를 제공하여 오토스케일링이 제공된다.

- **어플리케이션 개발 단순화**

개발환경과 배포환경을 동일시 할 수 있기에 개발이 용이해지며, 롤백을 제공하기에 개발자들이 좀 더 과감하게 배포할 수 있다.

## 요약

- 모놀리스 어플리케이션은 구축하기 쉽지만 시간이 지남에 따라 유지관리가 어려워진다.
- MSA기반 어플리케이션 아키텍쳐는 각 구성요소의 개발을 용이하게 하지만, 하나의 시스템으로 작동하도록 배포하고 구성하기가 어렵다.
- 리눅스 컨테이너는 가상머신과 동일한 이점을 제공하지만 훨씬 더 가볍고 하드웨어 활용도를 높일 수 있다.
- 도커는 `OS`환경과 함께 컨테이너화된 어플리케이션을 좀 더 쉽고 빠르게 관리할 수 있는 리눅스 컨테이너 기술을 개선했다.
- 쿠버네티스는 데이터 센터 전체를 어플리케이션 실행을 위한 컴퓨팅 리소스로 제공한다.
- 개발자는 시스템의 도움 없이도 쿠버네티스로 어플리케이션 배포할 수 있다.
- 시스템 관리자는 고장 난 노드를 쿠버네티스가 자동으로 처리하게 함으로써 꿀잠잘 수 있다.

# 2장 도커와 쿠버네티스 첫 걸음

_책에서는 도커 이미지 빌드, 도커파일 작성, 도커 캐싱, 도커 파일 시스템 찾아보기, 컨테이너 중지 및 시작 명령어, 이미지 레지스트리 푸시, 태그 지정 등 도커에 관련된 내용이 포함되어 있지만 이는 쿠버네티스에 대한 내용이 아님으로 패스_

## 쿠버네티스 클러스터

`Minkube`를 활용해 단일 노드 클러스터의 예제를 진행

- 클러스터 정보 조회

```
./kubectl cluster-info
```

- 클러스터 위의 모든 노드 조회

```
./kubectl get nodes
```

- 노드 정보 디테일 조회

```c
./kubectl descrbie node <노드이름>

# 모든 노드 정보 조회
./kubectl descrbie node 
```

> 쿠버네티스는 개별 컨테이너를 직접 다루지 안흔다. 콘테이너는 포드 위에서 동작하게 되고, 쿠버네티스에서는 해당 파드를 조회해야 한다.

```
./kubectl get pods
```
동일하게 `descrbie pods`를 통해 포드의 상세정보를 조회할 수 있다.

---

해당 `kubectl`의 동작과정은 다음과 같다.

1. 쿠버네티스의 `API`서버로 `REST HTTP`요청을 전달하고 클러스터에 새로운 레플리케이션컨트롤러 오브젝트를 생성한다.
2. 레플리케이션컨트롤러는 새파드를 생성하고 스케줄러에 의해 워커 노드 중 하나에 스케줄링된다.
3. 해당 노드는 이미지가 로컬에 존재하지 않기에 레지스트리에서 풀을 받고 컨테이너를 생성하고 실행한다.

### 실행중인 파드에 접근하기

각 파드는 자체 `IP`주소를 가지고 있지만 이는 클러스터 내부의 가상 `IP`주소이고, 외부에서 접근이 불가능하다. 

외부에서 파드에 접근하고자 한다면 서비스 오브젝트를 생성해야한다.(Load Balancer 유형) `LoadBalancer`유형의 서비스를 생성하면 외부 로드 밸런서가 생성되므로 로드 밸런서의 퍼블릭 `IP`를 통해 파드에 연결할 수 있다.

서비스를 조회하는 명령어는 다음과 같다.

```
./kubectl get services
./kubectl get svc
```

`NAME                                                        TYPE           CLUSTER-IP       EXTERNAL-IP      PORT(S)           AGE`와 같은 값이 노출되게 되며 외부 `IP`를 통해 포드에 접근할 수 있다.

레플리카가 여러개 있어도 단일 엔드포인트로 접근 가능한 `API`서버를 통해 상호작용하고 있기 때문에 큰 상관은 없다.

아래는 단일 엔드포인트까지 접근의 요약이다.

1. `kubectl run`또는 파이프라인을 활용해 디플로이먼트를 배포하고자 한다.
2. 레플리케이션컨트롤러가 생성되고, 이는 실제 파드를 생성한다.
3. 클러스터 외부에서 파드에 접근가능하게 하기 위해서 쿠버네티스에게 레플리케이션컨트롤러에 의해 관리되는 모든 파드를 단일 서비스로 노출하도록 명령한다. (로드밸런서 서비스)

### 파드와 컨테이너에 대한 이해

파드는 하나 이상의 컨테이너를 포함하며 파드내부의 컨테이너들은 쿠버네티스 노드위의 동일한 볼륨의 파일시스템, 네트워크 망을 공유한다. 

파드는 자체의 고유한 사설 IP주소와 호스트 이름을 갖는다.

즉, 한 포드 위의 두 개 이상의 컨테이너는 `localhost`를 통해 접근이 가능하다.

### 레플리케이션컨트롤러의 역할

레플리케이션컨트롤러는 선언적으로 선언된 스펙에 따라 포드들을 관리한다. 

### 서비스가 필요한 이유

파드는 일시적이다. 어넺든 사라지고 재시작될 수 있다. 이러한 상황에서 앞서 말한대로 레플리케이션컨트롤러가 새로운 파드를 지정된 스펙으로 관리하며 돌아간다. 

> 새로운 파드는 항상 새로운 `IP`주소를 할당받기에 이것이 서비스가 필요한 이유이다. 항상 변경되는 `IP`주소와 여러 파드의 `IP`를 단일 `IP`와 포트의 쌍으로 노출시키는 것이 서비스이다.

서비스가 생성되면 정적 `IP`를 할당받고 서비스가 존속하는 동안 변경되지 않는다. 

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app.kubernetes.io/name: MyApp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
```


### 어플리케이션 수평 확장

쿠버네티스의 경우 어플리케이션은 레플리케이션컨트롤러에의해 모니터링되고 실행되며 서비스를 통해 외부에 노출된다.

이런 레플리케이션컨트롤러를 활용하면 간단하게 수평확장할 수 있다.

```c
kubectl scale rc kubia --replicas=3
```

이는 선언적으로 인스턴스를 3개로 선언했으며 쿠버네티스는 현재의 상태를 검사해 의도한 상태로 조정한다.

이렇게 여러개 뜬 포드는 서비스(로드밸런서)에 의해 요청이 분산되게 된다.

## 어플리케이션이 실행 중인 노드 검사하기

```c
./kubectl get pods -o wide
```

명령어를 통해 파드가 어떤 노드에 스케줄링되었고, 어떤 IP를 가지고 있는지 알 수 있다.

하지만 이렇게 CLI말고도 웹 대시보드도 제공하고 있다.

- `GKE`

```c
./kubectl cluster-info | grep dashboard
```

## 요약

- 포드내 컨테이너는 이미지 레지스트리에서 이미질을 풀하여 실행할 수 있다.
- 실행 중인 컨테이너에 `exec`명령어를 통해 접속할 수 있다.
- `GKE`에 다중 노드 쿠버네티스 클러스터를 설정할 수 있다.
- 쿠버네티스 클러스터의 노드, 파드, 서비스, 레플리케이션, hpa 등을 검색할 수 있다.
- 쿠버네티스의 컨테이너를 실행하고 외부에서 접근 가능하게할 수 있다. (Service)
- 레플리카 수를 수평적으로 확장할 수 있다.

# 3장 파드, 쿠버네티스에서 컨테이너 실행

## 파드 소개

> 파드는 컨테이너의 그룹이며 쿠버네티스의 기본 빌딩 블록이다.

컨테이너를 개별적으로 배포하지 않고 파드를 배포하고 운영한다. (일반적으로 파드는 하나의 컨테이너만 포함한다.)

모든 컨테이너는 항상 하나의 워커 노드에서 실행되며 여러 노드에 걸쳐 실행되지 않는다.

![](https://velog.velcdn.com/images/cksgodl/post/d59954e6-e09a-45d1-b9f9-9d3f61a09a39/image.png)

### 왜 이렇게 파드를 구성할까?

왜 컨테이너를 직접 조율하지않고 쿠버네티스는 파드를 구성하여 운영할까?

#### 여러 프로세스를 실행하는 단일 컨테이너보다 다중 컨테이너가 낫다.

`IPC`혹은 로컬 파일을 통해 통신하는 여러 프로세스로 구성돼, 같은 노드에서 실행해야할 때, 쿠버네티스 상 컨테이너 하나를 실행하고, 컨테이너 하나에서 여러 프로세스를 실행하면 되는 것 아닌가? 이라고 생각할 수 있다.

> 하지만, 컨테이너는 단일 프로세스를 실행하는 것을 목적으로 설계되었다. 

다중 프로세스를 구성할 경우 개별 프로세스가 실패하는 경우 자동으로 재시작하는 메커니즘을 사용자가 책임져야하며, 다중프로세스에 대한 로그 또한 사용자가 책임져야 한다. 

따라서 각 프로세스를 자체의 개별로 컨테이너로 실행해야 한다. 이것이 쿠버네티스와 도커를 사용하는 방법이다.

## 파드 이해하기

여러 프로세스를 단일 컨테이너로 묶지 않기 때문에, 컨테이너를 함께 묶고 하나의 단위로 관리할 수 있는 또 다른 상위 구조가 필요하다. 이것이 파드이다.

#### 같은 파드에서 컨테이너 간 부분 격리

그룹안에 있는 컨테이너는 네트워크 망을 공유한다. 따라서 쿠버네티스는 파드 안의 모든 커넽이너가 자체 네임스페이스가 아닌 동일한 리눅스 네임스페이스를 공유하도록 도커를 설정한다.

또한 파드의 모든 컨테이너는 동일한 `IPC` 네임스페이스 아래에서 실행돼 `IPC`를 통해 서로 통신할 수 있다. 최신 쿠버네티스와 도커에서는 동일한 `PID` 네임스페이스를 공유할 수 있지만, 기본적으로 활성화돼 있지는 않다.

하지만, 파일시스템에 한해지는 사정이 족므 다르다. 컨테이너의 파일시스템은 컨테이너 이미지에서 나오기 때문에, 기본적으로 파일 시스템은 다른 컨테이너와 완전히 분리된다. 그래도 쿠버네티스의 볼륨 개념을 이용해 컨테이너가 파일 디렉터리를 공유하는 것이 가능하다.

#### 컨테이너가 동일한 IP와 포트 공간을 공유하는 방법

파드안의 컨테이너들은 동일한 네트워크 네임스페이스에서 실행되기 때문에, 컨테이너간은 동일한 IP주소와 포트 공간을 공유한다. (컨테이너간 같은 포트 번호를 사용하면 안된다.) 

#### 파드 간 플랫 네트워크

쿠버네티스간의 통신은 `LAN`에 있는 컴퓨터간의 통신과 비슷하다. `LAN`상의 컴퓨터는 각 포드처럼 고유`IP`를 가지며 모든 다른 파드에서 이 네트워크를 통해 접속할 수 있다. (물리 네트워크 계층 위에 추가적인 소프트웨어 정의 네트워크 계층을 정의한다.)

![](https://velog.velcdn.com/images/cksgodl/post/81add6fe-1c90-49df-ab16-3061dc99d998/image.png)

## 파드에서 컨테이너의 적절한 구성

프론트 앱과 백엔드 앱으로 구성된 다중 어플리케이션을 단일 파드보단 2개의 파드로 구성해야 한다. 파드는 상대적으로 가볍기 때문에 오버헤드 없이 필요한 만큼 생성할 수 있고, 하나의 파드는 되도록 간단하게 구성해야 한다.

#### 다계층 어플리케이션을 여러 파드로 분할

노드가 2개인데 파드를 하나만 쓰면 한개의 노드가 놀 수 있다. 이는 OS의 페이징 이슈과 비슷하며 파드의 오버헤드는 적기 때문에 되도록 작게 분할하는 것이 좋다.

#### 개별 확장이 가능한 다중 파드

다중 파드를 권장하는 이유 중 스케일링이슈도 있다. 파드는 스케일링의 기본 단위이다. 쿠버네티스는 개별 컨테이너를 수평으로 확장할 수 없다. 대신 전체 파드를 수평으로 확장한다. 

다중 프로세스를 실행하는 어플리케이션을 수평적으로 확장하게 된다면 리소스 낭비가 심할 것 이다.

#### 파드에서 여러 컨테이너를 사용하는 경우

![](https://velog.velcdn.com/images/cksgodl/post/7e921438-4344-4a78-958f-1de615689683/image.png)

어플리케이션이 하나의 주소 프로세스와 하나 이상의 보완 프로세스로 구성된 경우에는 다중 컨테이너를 활용할 수 있다.

ex) 로그 수집기, 데이터 프로세서, 통신 어댑터 등등

#### 파드에서 여러 컨테이너를 사용하는 경우 결정

다중 컨테이너를 사용하고자 할 때 다음과 같은 사항을 고려하자.

- 컨테이너를 함께 실행해야 하는가, 혹은 서로 다른 호스트에서 실행할 수 있는가?
- 여러 컨테이너가 모여 하나의 구성 요소를 나타내는가, 혹은 개별적인 구성요소인가?
- 컨테이너가 함께, 혹은 개별적으로 스케일링 되어야 하는가?

> 되도록이면 작은 포드를 유지하라.


## YAML, JSON 디스크립터로 파드 생성

쿠버네티스는 리소스를 일반적으로 쿠버네티스 `REST API`엔드 포인트에 `JSON` 혹은 `YAML`매니페스트를 전송해 생성한다.

`kubectl run`명령어 처럼 간단하게 리소스를 만들 수도 있지만, `YAML`파일을 통해 버전 관리 시스템에 넣는 것이 가능해진다.

쿠버네티스 `API`의 리소스는 정말 다양하며, 자세한 내용은 해당 부분에서 다루지 않는다.

```yaml
$ kubectl get po kubia-zxzij -o yaml

apiVersion: v1 # 쿠버네티스 API 버전
kind: Pod	   # 오브젝트 유형
metadata:	   # 파드의 메타 데이터(HPA, 라벨검색 등에 활용)
    annotations:
        kubernetes.io/created-by: ...
    creationTimestamp: 2016-03-18T12:37:50Z
    generateName: kubia-
    labels:
        run: kubia
    name: kubia-zxzij
    namespace: default
    resourceVerion: "294"
    selfLink: /api/v1/namespaces/default/pods/kubia-zxzij
    uid: 3a564c0-ed06-11e5-ba3b-42010af0004
spec:		 # 파드의 스펙(컨테이너 볼륨 등, 상태)
    containers:
    - image: luksa/kubia
      imagePullPolicy: IfNotPresent
      name: kubia
      ports:
      - containerPort: 8080
        protocol: TCP
      resources:
         requests
            cpu: 100m
         volumeMounts:
         - mountPath: /var/run/secrets/k8s.io/servacc
           name: default-token-kvcqa
           readOnly: true
    dnsPolicy: ClusterFirts
    nodeNAme: gke-kubia-e8fe08b8-node-txje
    restartPolicy: Always
    serviceAccount: default
    terminationGracePeriodSeconds: 30
    volumes:
    - name: default-token-kvcqa
      secret:
          secretName: default-token-kvcqa
    conditions:
    - lastProbeTiem: null
      lastTransitionTime: null
      status: "True"
      type: Ready
   containerStatuses:
   - containerID: docker://f0276994322d247ba...
      image: luksa/kubia
      imageID: docker://4c325bcc640c.....
      lastState: {}
      name: kubia
      ready: true
      restartCount: 0
      state:
         running:
              startAt: 2016-03-18T12:46:05Z
hostIP: 10.132.0.4
phase: Running
podIP: 10.0.2.3
startTime: 2016-03-18T12:44:32Z
```

이렇게 `YAML`파일을 직접 작성할 수도 있지만, `Helm`이란 오픈소스를 통해 차트의 형식으로 쿠버네티스상의 리소스를 더 간편하게 관리할 수 있다.

#### 파드를 정의하는 주요 부분

- Metadata : 이름, 네임스페이스, 레이블 및 파드에 관한 기타 정보
- Spec : 파드 컨테이너, 볼륨, 기타 데이터 등 파드 자체에 관한 실제 명세
- Status : 파드 상태, 각 컨테이너 설명과 상태, 파드 내부 IP, 기타 기본 정보 등 현재 실행 중인 파드에 관한 정보

#### kubectl cerate 명령을 통해 파드 만들기

```c
./kubectl create -f kubia-manual.yaml
```

해당 명령어를 통해 리소스를 만들 수 있다.

#### 로그 보기

```c
./kubectl logs kubia-manual

./kubectl logs kubia-manual -c kubia
```

포드에 대한 로그를 볼 수도 있으며, 각각의 컨테이너에 대한 로그도 볼 수 있다.

현존하는 컨테이너의 로그만 가져올 수 있다. 파드가 삭제되면 해당 로그도 같이 삭제된다.

## 파드에 요청 보내기

서비스를 활용하지 않고도 파드에 테스트와 디버깅 목적으로 연결할 수 있는 방법이 있다. 바로 __포트포워딩__이다.

#### 로컬 네트워크 포트를 다른 포트로 포워딩

쿠버네티스는 해당 파드로 향하는 포트 포워딩을 구성해준다. 포드 포워딩 구성은

```c
./kubectl port-forward kubia-manual 8888:8080
```

과 같이 작성할 수 있다.

위의 명령어는 머신의 로컬 포트 8888을 `kubia-manual`파드의 8080포드로 향하게 한다.

![](https://velog.velcdn.com/images/cksgodl/post/11895ef2-bbf1-4097-bda6-054353eff56b/image.png)

## 파드의 레이블에 대하여

실제 어플리케이션을 배포할 때 대부분의 사용자는 더 많은 파드를 실행하게 된다. 파드 수가 증가함에 따라 파드를 분류집합으로 분류할 필요가 있다.

예를 들어 마이크로서비스 아키텍쳐의 경우 배포된 마이크로서비스의 수는 매우 쉽게 20개를 초과한다. 또한 여러 버전 혹은 릴리스(베타, 릴리즈, 카나리 등)이 동시에 실행된다. 이에 따라 시스템에 수백 개의 파드가 생길 수 있다. 

![](https://velog.velcdn.com/images/cksgodl/post/d4906332-1c48-403f-b32d-ecd912676a92/image.png)

개발자와 시스템은 가각의 파드를 구별할 수 있는 라벨을 달 수 있으면 좋을 것 이다.

### 라벨(레이블) 이란?

라벨은 파드와 모든 다른 쿠버네티스 리소스를 조직화할 수 있는 단순하고 강력한 쿠버네티스 기능이다.

이는 메타데티어 작성하는 키-값 쌍으로, 이 쌍은 레이블 설렉터를 사용해 리소스를 선택할 때 활용된다. 레이블 키가 해당 리소스 내에서 고유하다면, 하나 이상 원하는 만큼 레이블을 가질 수 있다. 

- 어플리케이션 이름
- 파드에서 실행 중인 어플리케이션 버전

등을 관리할 수 있다.

#### 레이블 지정하는 방법

```yaml
apiVersion: v1 # 쿠버네티스 API 버전
kind: Pod	   # 오브젝트 유형
metadata:	   # 파드의 메타 데이터(HPA, 라벨검색 등에 활용)
    annotations:
        kubernetes.io/created-by: ...
    creationTimestamp: 2016-03-18T12:37:50Z
    generateName: kubia-
    labels:			# 라벨
        run: kubia
        ...
```

아래 명령어를 통해 라벨을 볼 수 있다.

```c
./kubectl get po --show-labels

./kubectl get po -L creation_method,env # 특정 라벨 조회
```

기존 파드 라벨 수정도 가능하다.

## 레이블 설렉터

#### 레이블 설랙터를 활용해 다음 작업을 수행할 수 있다.

- 리소스를 조회하거나
- 삭제
- 특정 노드 스케줄링 제한 또는 특정 노드에 스케줄링


#### 레이블설렉터가 레이블을 선택할 때 조건은 아래 와 같다.

- 특정 키를 포함하거나 포함하지 않는 레이블

`creation_method`를 가지고 있는 파드 중에 값이 manual이 아닌 것
```
creation_mothid!=manual
```

- 특정한 키와 값을 가진 레이블

env 레이블 값이 prod 또는 devel로 설정돼 있는 파드
```
env in (prod,devel)
```

- 특정한 키를 갖고 있지만, 다른 값을 가진 레이블

env 레이블 값이 prod, devel이 아닌 파드
```
env notin (prod,devel)
```

## 어노테이션

어노테이션은 키-값 쌍으로 레이블과 비슷하지만, 식별 정보를 가지지 않는다. 레이블은 오브젝트(리소스)를 묶는데 사용되지만, 어노테이션은 그렇게 할 수 없다. 

레이블설렉터를 통해서 오브젝트를 선택하는 것이 가능하지만 어노테이션 설렉터와 같은 것은 없다.

> 어노테이션은 오브젝트(쿠버네티스 리소스)에 설명을 추가하는 경우 사용된다.

## 네임스페이스를 통한 리소스 그룹화

오브젝트를 그룹으로 분할하고자 할 때 네임스페이스를 사용할 수 있다. 이는 리눅스 네임스페이스와 다르며, 쿠버네티스 네임스페이스는 오브젝트 이름의 범위를 제공한다.

분리된 네임스페이스는 같은 리소스 이름을 다른 네임스페이스에 걸쳐 여러 번 사용할 수 있게 해준다.

- 네임스페이스 조회

```
./kubectl get ns
```

> 네트워크 격리를 제공하는지는 쿠버네티스의 네트워킹 솔루션에 따라 다르다. `foo` 네임스페이스의 파드가 `bar`네임스페이스의 파드의 주소를 알고 있따면 트래픽을 보낼 수 있다.

## 요약

- 특정 컨테이너를 파드로 묶어야 하는가? (멀티 프로세스와 멀티 파드)
- 파드는 여러 프로세스를 실행할 수 있으며, 컨테이너가 아닌 세계의 물리적 호스트와 비슷
- YAML 디스크립터를 작성해 파드를 작성하고 파드 정의와 상태를 확인할 수 있다.(Heml)
- 레이블과 레이블 설렉터를 활용해 파드를 그룹으로 조작할 수 있다. (스케줄링, 삭제)
- 네임스페이스는 다른 팀들이 동일한 클러스터를 별도 클러스터를 사용하는 것처럼 이용하게 해준다.
- `kubectl explain`명령어로 리소스를 빠르게 찾을 수 있다.


