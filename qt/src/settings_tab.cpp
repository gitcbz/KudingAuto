#include "settings_tab.h"
#include "backend_client.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QMessageBox>
#include <QSettings>

SettingsTab::SettingsTab(BackendClient *backend, QWidget *parent)
    : QWidget(parent), backend(backend) {
    setupUI();
    loadSettings();
}

void SettingsTab::setupUI() {
    QVBoxLayout *mainLayout = new QVBoxLayout(this);

    // 解密设置
    QLabel *decryptTitle = new QLabel("Decryption Settings");
    decryptTitle->setStyleSheet("font-weight: bold; font-size: 14px;");
    mainLayout->addWidget(decryptTitle);

    // API URL 设置
    QHBoxLayout *urlLayout = new QHBoxLayout();
    QLabel *urlLabel = new QLabel("Local API URL:");
    apiUrlEdit = new QLineEdit();
    apiUrlEdit->setPlaceholderText("https://kddecode.api.cbzstudio.qzz.io");
    urlLayout->addWidget(urlLabel);
    urlLayout->addWidget(apiUrlEdit);

    QPushButton *saveBtn = new QPushButton("Save");
    connect(saveBtn, &QPushButton::clicked, this, &SettingsTab::onSaveSettings);
    urlLayout->addWidget(saveBtn);
    mainLayout->addLayout(urlLayout);

    // Debug 模式
    debugModeCheck = new QCheckBox("Debug Mode (verbose logging)");
    connect(debugModeCheck, &QCheckBox::toggled, this, &SettingsTab::onDebugModeToggled);
    mainLayout->addWidget(debugModeCheck);

    // 语言选择
    QHBoxLayout *langLayout = new QHBoxLayout();
    QLabel *langLabel = new QLabel("Language:");
    languageCombo = new QComboBox();
    languageCombo->addItems({"English", "中文"});
    connect(languageCombo, QOverload<const QString &>::of(&QComboBox::currentTextChanged),
            this, &SettingsTab::onLanguageChanged);
    langLayout->addWidget(langLabel);
    langLayout->addWidget(languageCombo);
    langLayout->addStretch();
    mainLayout->addLayout(langLayout);

    // OCR 模式选择
    QHBoxLayout *ocrLayout = new QHBoxLayout();
    QLabel *ocrLabel = new QLabel("OCR Engine:");
    ocrModeCombo = new QComboBox();
    ocrModeCombo->addItems({"PaddleOCR", "EasyOCR", "Tesseract"});
    connect(ocrModeCombo, QOverload<const QString &>::of(&QComboBox::currentTextChanged),
            this, &SettingsTab::onOCRModeChanged);
    ocrLayout->addWidget(ocrLabel);
    ocrLayout->addWidget(ocrModeCombo);
    ocrLayout->addStretch();
    mainLayout->addLayout(ocrLayout);

    // 说明文字
    QLabel *infoLabel = new QLabel(
        "Decryption Settings:\n\n"
        "The application uses a Python backend to handle API requests.\n"
        "Make sure the backend server is running on the specified URL.\n\n"
        "API URL: The address of your decryption server.\n"
        "OCR Engine: Choose the OCR engine for captcha recognition."
    );
    infoLabel->setStyleSheet("color: #666; font-size: 10px;");
    infoLabel->setWordWrap(true);
    mainLayout->addWidget(infoLabel);

    mainLayout->addStretch();
}

void SettingsTab::loadSettings() {
    QSettings settings("KudingJudge", "KudingJudge");
    apiUrlEdit->setText(settings.value("api_url", "http://127.0.0.1:5000").toString());
    debugModeCheck->setChecked(settings.value("debug_mode", false).toBool());
    languageCombo->setCurrentText(settings.value("language", "English").toString());
    ocrModeCombo->setCurrentText(settings.value("ocr_engine", "PaddleOCR").toString());
}

void SettingsTab::onSaveSettings() {
    QSettings settings("KudingJudge", "KudingJudge");
    settings.setValue("api_url", apiUrlEdit->text());
    settings.setValue("debug_mode", debugModeCheck->isChecked());
    settings.setValue("language", languageCombo->currentText());
    settings.setValue("ocr_engine", ocrModeCombo->currentText());

    QMessageBox::information(this, "Success", "Settings saved successfully!");
}

void SettingsTab::onDebugModeToggled(bool checked) {
    // 处理 Debug 模式切换
}

void SettingsTab::onLanguageChanged(const QString &language) {
    // 处理语言切换
}

void SettingsTab::onOCRModeChanged(const QString &mode) {
    // 处理 OCR 模式切换
}
