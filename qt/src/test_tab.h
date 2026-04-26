#ifndef TEST_TAB_H
#define TEST_TAB_H

#include <QWidget>
#include <QLineEdit>
#include <QComboBox>
#include <QPushButton>
#include <QPlainTextEdit>

class BackendClient;

class TestTab : public QWidget {
    Q_OBJECT

public:
    explicit TestTab(BackendClient *backend, QWidget *parent = nullptr);

private slots:
    void onLanguageChanged(const QString &language);
    void onBrowseCode();
    void onLoadInput();
    void onSubmit();
    void onSubmitResult(bool success, int judgeId, const QString &message);

private:
    void setupUI();

    BackendClient *backend;
    QComboBox *languageCombo;
    QLineEdit *codeFileEdit;
    QPushButton *browseBtn;
    QPlainTextEdit *inputEdit;
    QPushButton *submitBtn;
};

#endif // TEST_TAB_H
