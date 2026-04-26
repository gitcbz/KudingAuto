#ifndef PROBLEM_TAB_H
#define PROBLEM_TAB_H

#include <QWidget>
#include <QLineEdit>
#include <QComboBox>
#include <QPushButton>
#include <QLabel>
#include <QCheckBox>
#include <QPixmap>

class BackendClient;
class CodeEditor;

class ProblemTab : public QWidget {
    Q_OBJECT

public:
    explicit ProblemTab(BackendClient *backend, QWidget *parent = nullptr);

private slots:
    void onGetCaptcha();
    void onRefreshCaptcha();
    void onSubmitModeChanged();
    void onBrowseCode();
    void onSubmit();
    void onCaptchaFetched(const QString &cid, const QPixmap &image);
    void onOCRResult(const QString &text);
    void onAutoOCRToggled(bool checked);
    void onSuperOCRToggled(bool checked);

private:
    void setupUI();
    void performOCR(bool enhanced = false);

    BackendClient *backend;
    QLineEdit *problemIdEdit;
    QComboBox *languageCombo;
    QPushButton *getCaptchaBtn;
    QLabel *captchaLabel;
    QPushButton *refreshBtn;
    QLineEdit *captchaEdit;
    QCheckBox *autoOCRCheck;
    QCheckBox *enhancedOCRCheck;
    QCheckBox *superOCRCheck;
    CodeEditor *codeEditor;
    QLineEdit *codeFileEdit;
    QPushButton *browseBtn;
    QPushButton *submitBtn;

    QString currentCid;
    QByteArray currentCaptchaData;
};

#endif // PROBLEM_TAB_H
