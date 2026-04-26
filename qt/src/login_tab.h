#ifndef LOGIN_TAB_H
#define LOGIN_TAB_H

#include <QWidget>
#include <QLineEdit>
#include <QPushButton>
#include <QLabel>
#include <QCheckBox>
#include <QPixmap>

class BackendClient;

class LoginTab : public QWidget {
    Q_OBJECT

public:
    explicit LoginTab(BackendClient *backend, QWidget *parent = nullptr);

private slots:
    void onRefreshCaptcha();
    void onLogin();
    void onCaptchaFetched(const QString &cid, const QPixmap &image);
    void onLoginResult(bool success, const QString &message);
    void onOCRResult(const QString &text);
    void onAutoOCRToggled(bool checked);
    void onSuperOCRToggled(bool checked);

private:
    void setupUI();
    void performOCR(bool enhanced = false);

    BackendClient *backend;
    QLineEdit *usernameEdit;
    QLineEdit *passwordEdit;
    QLineEdit *captchaEdit;
    QPushButton *loginBtn;
    QPushButton *refreshBtn;
    QLabel *captchaLabel;
    QCheckBox *rememberCheck;
    QCheckBox *autoOCRCheck;
    QCheckBox *enhancedOCRCheck;
    QCheckBox *superOCRCheck;

    QString currentCid;
    QByteArray currentCaptchaData;
};

#endif // LOGIN_TAB_H
