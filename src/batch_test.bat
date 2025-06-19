FOR /F "tokens=* USEBACKQ" %%g IN (`git branch --show-current`) do (SET "BRANCH_NAME=%%g")

@echo %BRANCH_NAME%

echo %BRANCH_NAME% | findstr /c:"/" ||(
    :: Commands to execute if condition is true
    echo You must checkout a branch in format {release_type}/{X.X.X}
    exit /b 2
)



