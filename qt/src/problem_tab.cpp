#include "problem_tab.h"
#include "backend_client.h"
#include "code_editor.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QFileDialog>
#include <QMessageBox>
#include <QFile>
#include <QRadioButton>
#include <QButtonGroup>

ProblemTab::ProblemTab(BackendClient *backend, QWidget *parent)
    : QWidget(parent), backend(backend) {
    setupUI();

    connect(backend, &BackendClient::captchaFetched, this, &ProblemTab::onCaptchaFetched);
    connect(backend, &BackendClient::ocrResult, this, &ProblemTab::onOCRResult);
}

void ProblemTab::setupUI() {
    QVBoxLayout *mainLayout = new QVBoxLayout(this);

    // 顶部：问题ID、语言、获取验证码
    QHBoxLayout *topLayout = new QHBoxLayout();

    QLabel *idLabel = new QLabel("Problem ID:");
    problemIdEdit = new QLineEdit();
    problemIdEdit->setPlaceholderText("e.g. 1000");
    problemIdEdit->setMaximumWidth(100);
    topLayout->addWidget(idLabel);
    topLayout->addWidget(problemIdEdit);

    QLabel *langLabel = new QLabel("Language:");
    languageCombo = new QComboBox();
    languageCombo->addItems({"cpp", "c", "py", "java"});
    languageCombo->setCurrentText("cpp");
    topLayout->addWidget(langLabel);
    topLayout->addWidget(languageCombo);

    getCaptchaBtn = new QPushButton("Get Captcha");
    connect(getCaptchaBtn, &QPushButton::clicked, this, &ProblemTab::onGetCaptcha);
    topLayout->addWidget(getCaptchaBtn);

    topLayout->addStretch();
    mainLayout->addLayout(topLayout);

    // 验证码区域
    QHBoxLayout *captchaLayout = new QHBoxLayout();

    QVBoxLayout *captchaLeftLayout = new QVBoxLayout();
    QLabel *captchaTitle = new QLabel("Captcha:");
    captchaLabel = new QLabel();
    captchaLabel->setMinimumSize(120, 60);
    captchaLabel->setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;");
    captchaLabel->setCursor(Qt::PointingHandCursor);
    connect(captchaLabel, &QLabel::linkActivated, this, &ProblemTab::onRefreshCaptcha);
    refreshBtn = new QPushButton("Refresh");
    connect(refreshBtn, &QPushButton::clicked, this, &ProblemTab::onRefreshCaptcha);
    captchaLeftLayout->addWidget(captchaTitle);
    captchaLeftLayout->addWidget(captchaLabel);
    captchaLeftLayout->addWidget(refreshBtn);
    captchaLeftLayout->addStretch();

    QVBoxLayout *captchaRightLayout = new QVBoxLayout();
    QLabel *codeLabel = new QLabel("Enter captcha:");
    captchaEdit = new QLineEdit();
    captchaEdit->setPlaceholderText("Enter captcha");
    captchaRightLayout->addWidget(codeLabel);
    captchaRightLayout->addWidget(captchaEdit);

    autoOCRCheck = new QCheckBox("Auto OCR");
    connect(autoOCRCheck, &QCheckBox::toggled, this, &ProblemTab::onAutoOCRToggled);
    captchaRightLayout->addWidget(autoOCRCheck);

    enhancedOCRCheck = new QCheckBox("OCR Enhanced");
    captchaRightLayout->addWidget(enhancedOCRCheck);

    superOCRCheck = new QCheckBox("Super OCR (~99% accuracy)");
    connect(superOCRCheck, &QCheckBox::toggled, this, &ProblemTab::onSuperOCRToggled);
    captchaRightLayout->addWidget(superOCRCheck);

    captchaRightLayout->addStretch();

    captchaLayout->addLayout(captchaLeftLayout);
    captchaLayout->addLayout(captchaRightLayout);
    mainLayout->addLayout(captchaLayout);

    // 代码编辑器
    QLabel *editorLabel = new QLabel("Code Editor:");
    mainLayout->addWidget(editorLabel);

    codeEditor = new CodeEditor();
    codeEditor->setCode("#include <iostream>\nusing namespace std;\nint main() {\n    // your code\n    return 0;\n}");
    codeEditor->setMinimumHeight(200);
    mainLayout->addWidget(codeEditor);

    // 提交方式选择
    QHBoxLayout *modeLayout = new QHBoxLayout();
    QRadioButton *editorRadio = new QRadioButton("Editor");
    QRadioButton *fileRadio = new QRadioButton("File");
    editorRadio->setChecked(true);
    modeLayout->addWidget(editorRadio);
    modeLayout->addWidget(fileRadio);
    modeLayout->addStretch();
    mainLayout->addLayout(modeLayout);

    // 文件选择
    QHBoxLayout *fileLayout = new QHBoxLayout();
    QLabel *fileLabel = new QLabel("Code file:");
    codeFileEdit = new QLineEdit();
    codeFileEdit->setPlaceholderText("Select code file");
    codeFileEdit->setText("test.cpp");
    codeFileEdit->setEnabled(false);
    browseBtn = new QPushButton("Browse...");
    browseBtn->setEnabled(false);
    connect(browseBtn, &QPushButton::clicked, this, &ProblemTab::onBrowseCode);
    fileLayout->addWidget(fileLabel);
    fileLayout->addWidget(codeFileEdit);
    fileLayout->addWidget(browseBtn);
    mainLayout->addLayout(fileLayout);

    // 提交按钮
    submitBtn = new QPushButton("Submit Problem");
    submitBtn->setMinimumHeight(40);
    mainLayout->addWidget(submitBtn);

    mainLayout->addStretch();
}

void ProblemTab::onGetCaptcha() {
    QString problemId = problemIdEdit->text().trimmed();
    if (problemId.isEmpty()) {
        QMessageBox::warning(this, "Warning", "Please enter problem ID");
        return;
    }

    backend->fetchProblemCaptcha();
}

void ProblemTab::onRefreshCaptcha() {
    backend->fetchProblemCaptcha();
}

void ProblemTab::onSubmitModeChanged() {
    // 处理编辑器/文件模式切换
}

void ProblemTab::onBrowseCode() {
    QString file = QFileDialog::getOpenFileName(this, "Select Code File",
        "", "Code Files (*.cpp *.c *.py *.java);;All Files (*)");

    if (!file.isEmpty()) {
        codeFileEdit->setText(file);
    }
}

void ProblemTab::onSubmit() {
    QString problemId = problemIdEdit->text().trimmed();
    if (problemId.isEmpty()) {
        QMessageBox::warning(this, "Warning", "Please enter problem ID");
        return;
    }

    QString code = codeEditor->getCode();
    if (code.isEmpty()) {
        QMessageBox::warning(this, "Warning", "Please enter code");
        return;
    }

    QString language = languageCombo->currentText();
    // 提交逻辑
}

void ProblemTab::onCaptchaFetched(const QString &cid, const QPixmap &image) {
    currentCid = cid;
    currentCaptchaData = QByteArray();

    QPixmap scaled = image.scaledToWidth(120, Qt::SmoothTransformation);
    captchaLabel->setPixmap(scaled);

    if (autoOCRCheck->isChecked()) {
        performOCR(enhancedOCRCheck->isChecked());
    }
}

void ProblemTab::onOCRResult(const QString &text) {
    captchaEdit->setText(text);
}

void ProblemTab::onAutoOCRToggled(bool checked) {
    if (checked && !captchaLabel->pixmap().isNull()) {
        performOCR(enhancedOCRCheck->isChecked());
    }
}

void ProblemTab::onSuperOCRToggled(bool checked) {
    if (checked && !captchaLabel->pixmap().isNull()) {
        performOCR(true);
    }
}

void ProblemTab::performOCR(bool enhanced) {
    backend->performOCR(currentCaptchaData, enhanced ? "enhanced" : "normal");
}
