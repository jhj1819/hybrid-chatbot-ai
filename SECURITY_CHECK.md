# 🔒 보안 검토 체크리스트

이 문서는 저장소를 public으로 전환하기 전에 확인해야 할 보안 사항을 정리한 것입니다.

## ✅ 완료된 검토 사항

### 1. .gitignore 설정 확인
- ✅ `.env` 파일이 `.gitignore`에 포함되어 있음
- ✅ `.env.local`, `.env.production` 등도 포함되어 있음
- ✅ 민감한 파일 확장자(`*.pem`, `*.key` 등)가 포함되어 있음

### 2. 코드 내 API 키 검토
- ✅ 모든 스크립트 파일의 API 키는 플레이스홀더만 사용됨
- ✅ 실제 API 키가 하드코딩되지 않음
- ✅ 스크립트에 명확한 주석 추가됨

### 3. Git 추적 파일 확인
- ✅ `.env` 파일이 Git 추적에서 제거됨 (`git rm --cached .env`)

## ⚠️ 추가 확인 필요 사항

### 1. Git 히스토리 확인

과거 커밋에 실제 API 키가 포함되어 있을 수 있습니다. 다음 명령어로 확인하세요:

```bash
# Git 히스토리에서 실제 API 키 패턴 검색
git log --all --source -p | grep -i "sk-[a-zA-Z0-9]\{20,\}"

# 또는 PowerShell에서:
git log --all --source -p | Select-String -Pattern "sk-[a-zA-Z0-9]{20,}"
```

**실제 키가 발견되면:**
1. 즉시 해당 키를 OpenAI에서 재발급하세요
2. Git 히스토리에서 제거하세요:
   ```bash
   # BFG Repo-Cleaner 사용 (권장)
   # 또는 git filter-branch 사용
   ```

### 2. 환경 변수 파일 확인

로컬에 `.env` 파일이 있다면 내용을 확인하세요:

```bash
# .env 파일이 Git에 추적되지 않는지 확인
git ls-files | grep .env

# 결과가 비어있어야 합니다
```

### 3. 배포 스크립트 확인

다음 스크립트 파일들이 플레이스홀더만 사용하는지 확인하세요:
- `deploy-ec2.sh`
- `ec2-user-data.sh`
- `ec2-user-data-docker.sh`
- `deploy.sh`
- `setup_env.sh`

모든 스크립트는 `sk-your-actual-openai-api-key-REPLACE-THIS` 같은 플레이스홀더만 사용해야 합니다.

## 🛡️ Public 전환 전 최종 체크리스트

- [ ] Git 히스토리에 실제 API 키가 없음
- [ ] `.env` 파일이 Git에 추적되지 않음
- [ ] 모든 스크립트에 플레이스홀더만 사용됨
- [ ] README에 보안 주의사항이 포함됨
- [ ] `.gitignore`가 올바르게 설정됨

## 📝 Public 전환 후 권장 사항

1. **환경 변수 관리**
   - 로컬 개발: `.env` 파일 사용 (Git에 커밋하지 않음)
   - 프로덕션: AWS Secrets Manager 또는 환경 변수 사용

2. **키 로테이션**
   - 정기적으로 API 키를 재발급
   - 키 사용량 모니터링

3. **접근 제어**
   - API 키에 최소 권한 원칙 적용
   - 사용량 제한 설정

4. **모니터링**
   - 비정상적인 API 사용 패턴 감지
   - 알림 설정

## 🚨 문제 발견 시 조치 사항

만약 실제 API 키가 발견되었다면:

1. **즉시 조치**
   - OpenAI 대시보드에서 해당 키 삭제/재발급
   - 모든 환경에서 키 업데이트

2. **Git 히스토리 정리**
   ```bash
   # BFG Repo-Cleaner 사용 (권장)
   bfg --replace-text passwords.txt
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   ```

3. **재검토**
   - 모든 파일 재검토
   - 보안 체크리스트 재확인

