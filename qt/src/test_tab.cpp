#include "test_tab.h"
#include "backend_client.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QFileDialog>
#include <QMessageBox>
#include <QFile>

TestTab::TestTab(BackendClient *backend, QWidget *parent)
    : QWidget(parent), backend(backend) {
    setupUI();

    connect(backend, &BackendClient::submitResult, this, &TestTab::onSubmitResult);
}

void TestTab::setupUI() {
    QVBoxLayout *mainLayout = new QVBoxLayout(this);

    // 语言和文件选择
    QHBoxLayout *topLayout = new QHBoxLayout();

    QLabel *langLabel = new QLabel("Language:");
    languageCombo = new QComboBox();
    languageCombo->addItems({"cpp", "c", "py", "java"});
    languageCombo->setCurrentText("cpp");
    connect(languageCombo, QOverload<const QString &>::of(&QComboBox::currentTextChanged),
            this, &TestTab::onLanguageChanged);
    topLayout->addWidget(langLabel);
    topLayout->addWidget(languageCombo);

    QLabel *fileLabel = new QLabel("Code file:");
    codeFileEdit = new QLineEdit();
    codeFileEdit->setPlaceholderText("Select code file");
    codeFileEdit->setText("test.cpp");
    browseBtn = new QPushButton("Browse...");
    connect(browseBtn, &QPushButton::clicked, this, &TestTab::onBrowseCode);
    topLayout->addWidget(fileLabel);
    topLayout->addWidget(codeFileEdit);
    topLayout->addWidget(browseBtn);

    mainLayout->addLayout(topLayout);

    // 输入数据
    QLabel *inputLabel = new QLabel("Input data:");
    mainLayout->addWidget(inputLabel);

    QHBoxLayout *inputBtnLayout = new QHBoxLayout();
    inputBtnLayout->addStretch();
    QPushButton *loadBtn = new QPushButton("Load");
    connect(loadBtn, &QPushButton::clicked, this, &TestTab::onLoadInput);
    inputBtnLayout->addWidget(loadBtn);
    mainLayout->addLayout(inputBtnLayout);

    inputEdit = new QPlainTextEdit();
    inputEdit->setPlaceholderText("Enter test input");
    inputEdit->setMinimumHeight(100);
    mainLayout->addWidget(inputEdit);

    // 提交按钮
    submitBtn = new QPushButton("Submit Test");
    submitBtn->setMinimumHeight(40);
    connect(submitBtn, &QPushButton::clicked, this, &TestTab::onSubmit);
    mainLayout->addWidget(submitBtn);

    mainLayout->addStretch();
}

void TestTab::onLanguageChanged(const QString &language) {
    QMap<QString, QString> defaultFiles = {
        {"cpp", "test.cpp"},
        {"c", "test.c"},
        {"py", "test.py"},
        {"java", "Main.java"}
    };

    codeFileEdit->setText(defaultFiles.value(language, "test.cpp"));
}

void TestTab::onBrowseCode() {
    QString file = QFileDialog::getOpenFileName(this, "Select Code File",
        "", "Code Files (*.cpp *.c *.py *.java);;All Files (*)");

    if (!file.isEmpty()) {
        codeFileEdit->setText(file);
    }
}

void TestTab::onLoadInput() {
    QString file = QFileDialog::getOpenFileName(this, "Select Input File",
        "", "Text Files (*.txt *.in);;All Files (*)");

    if (!file.isEmpty()) {
        QFile f(file);
        if (f.open(QIODevice::ReadOnly | QIODevice::Text)) {
            inputEdit->setPlainText(QString::fromUtf8(f.readAll()));
            f.close();
        }
    }
}

void TestTab::onSubmit() {
    QString codePath = codeFileEdit->text().trimmed();
    QString language = languageCombo->currentText();
    QString input = inputEdit->toPlainText();

    if (codePath.isEmpty()) {
        QMessageBox::warning(this, "Warning", "Please select code file");
        return;
    }

    QFile codeFile(codePath);
    if (!codeFile.open(QIODevice::ReadOnly | QIODevice::Text)) {
        QMessageBox::critical(this, "Error", "Cannot open code file");
        return;
    }

    QString code = QString::fromUtf8(codeFile.readAll());
    codeFile.close();

    submitBtn->setEnabled(false);
    backend->submitTest(code, input, language);
}

void TestTab::onSubmitResult(bool success, int judgeId, const QString &message) {
    submitBtn->setEnabled(true);

    if (success) {
        QMessageBox::information(this, "Success", QString("Submit successful! Judge ID: %1").arg(judgeId));
    } else {
        QMessageBox::critical(this, "Failed", message);
    }
}
