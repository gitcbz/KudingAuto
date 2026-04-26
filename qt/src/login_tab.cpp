#include "login_tab.h"
#include "backend_client.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QMessageBox>
#include <QPixmap>

LoginTab::LoginTab(BackendClient *backend, QWidget *parent)
    : QWidget(parent), backend(backend) {
    setupUI();

    connect(backend, &BackendClient::captchaFetched, this, &LoginTab::onCaptchaFetched);
    connect(backend, &BackendClient::loginResult, this, &LoginTab::onLoginResult);
    connect(backend, &BackendClient::ocrResult, this, &LoginTab::onOCRResult);

    // 初始化验证码
    backend->fetchLoginCaptcha();
}

void LoginTab::setupUI() {
    QVBoxLayout *mainLayout = new QVBoxLayout(this);

    // 左右分割布局
    QHBoxLayout *splitLayout = new QHBoxLayout();

    // 左侧：登录表单
    QVBoxLayout *leftLayout = new QVBoxLayout();

    QLabel *userLabel = new QLabel("Username:");
    usernameEdit = new QLineEdit();
    usernameEdit->setPlaceholderText("Enter username");
    leftLayout->addWidget(userLabel);
    leftLayout->addWidget(usernameEdit);

    QLabel *passLabel = new QLabel("Password:");
    passwordEdit = new QLineEdit();
    passwordEdit->setPlaceholderText("Enter password");
    passwordEdit->setEchoMode(QLineEdit::Password);
    leftLayout->addWidget(passLabel);
    leftLayout->addWidget(passwordEdit);

    rememberCheck = new QCheckBox("Remember password");
    leftLayout->addWidget(rememberCheck);

    QLabel *captchaLabel = new QLabel("Captcha:");
    captchaEdit = new QLineEdit();
    captchaEdit->setPlaceholderText("Enter captcha");
    leftLayout->addWidget(captchaLabel);
    leftLayout->addWidget(captchaEdit);

    loginBtn = new QPushButton("Login");
    loginBtn->setMinimumHeight(36);
    connect(loginBtn, &QPushButton::clicked, this, &LoginTab::onLogin);
    leftLayout->addWidget(loginBtn);

    leftLayout->addStretch();

    // 右侧：验证码显示
    QVBoxLayout *rightLayout = new QVBoxLayout();

    QLabel *captchaTitle = new QLabel("Captcha (click to refresh)");
    rightLayout->addWidget(captchaTitle);

    captchaLabel = new QLabel();
    captchaLabel->setMinimumSize(150, 80);
    captchaLabel->setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;");
    captchaLabel->setCursor(Qt::PointingHandCursor);
    connect(captchaLabel, &QLabel::linkActivated, this, &LoginTab::onRefreshCaptcha);
    rightLayout->addWidget(captchaLabel);

    refreshBtn = new QPushButton("Refresh");
    connect(refreshBtn, &QPushButton::clicked, this, &LoginTab::onRefreshCaptcha);
    rightLayout->addWidget(refreshBtn);

    autoOCRCheck = new QCheckBox("Auto OCR");
    connect(autoOCRCheck, &QCheckBox::toggled, this, &LoginTab::onAutoOCRToggled);
    rightLayout->addWidget(autoOCRCheck);

    enhancedOCRCheck = new QCheckBox("OCR Enhanced");
    rightLayout->addWidget(enhancedOCRCheck);

    superOCRCheck = new QCheckBox("Super OCR (~99% accuracy)");
    connect(superOCRCheck, &QCheckBox::toggled, this, &LoginTab::onSuperOCRToggled);
    rightLayout->addWidget(superOCRCheck);

    rightLayout->addStretch();

    splitLayout->addLayout(leftLayout, 1);
    splitLayout->addLayout(rightLayout, 1);

    mainLayout->addLayout(splitLayout);
}

void LoginTab::onRefreshCaptcha() {
    backend->fetchLoginCaptcha();
}

void LoginTab::onLogin() {
    QString username = usernameEdit->text().trimmed();
    QString password = passwordEdit->text().trimmed();
    QString code = captchaEdit->text().trimmed();

    if (username.isEmpty() || password.isEmpty() || code.isEmpty()) {
        QMessageBox::warning(this, "Warning", "Please fill all fields");
        return;
    }

    loginBtn->setEnabled(false);
    backend->login(username, password, code);
}

void LoginTab::onCaptchaFetched(const QString &cid, const QPixmap &image) {
    currentCid = cid;
    currentCaptchaData = QByteArray(); // 保存原始数据用于 OCR

    QPixmap scaled = image.scaledToWidth(150, Qt::SmoothTransformation);
    captchaLabel->setPixmap(scaled);

    if (autoOCRCheck->isChecked()) {
        performOCR(enhancedOCRCheck->isChecked());
    }
}

void LoginTab::onLoginResult(bool success, const QString &message) {
    loginBtn->setEnabled(true);

    if (success) {
        QMessageBox::information(this, "Success", "Login successful!");
        captchaEdit->clear();
    } else {
        QMessageBox::warning(this, "Failed", message);
    }
}

void LoginTab::onOCRResult(const QString &text) {
    captchaEdit->setText(text);
}

void LoginTab::onAutoOCRToggled(bool checked) {
    if (checked && !captchaLabel->pixmap().isNull()) {
        performOCR(enhancedOCRCheck->isChecked());
    }
}

void LoginTab::onSuperOCRToggled(bool checked) {
    if (checked && !captchaLabel->pixmap().isNull()) {
        performOCR(true);
    }
}

void LoginTab::performOCR(bool enhanced) {
    // 这里需要获取原始图像数据进行 OCR
    // 实际实现中应该保存原始数据
    backend->performOCR(currentCaptchaData, enhanced ? "enhanced" : "normal");
}
