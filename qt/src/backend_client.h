#ifndef BACKEND_CLIENT_H
#define BACKEND_CLIENT_H

#include <QObject>
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QString>
#include <QPixmap>
#include <memory>

class QNetworkReply;

class BackendClient : public QObject {
    Q_OBJECT

public:
    explicit BackendClient(QObject *parent = nullptr);
    ~BackendClient();

    // 验证码相关
    void fetchLoginCaptcha();
    void fetchProblemCaptcha();

    // OCR 相关
    void performOCR(const QByteArray &imageData, const QString &mode = "normal");

    // 登录相关
    void login(const QString &username, const QString &password, const QString &code);

    // 提交相关
    void submitTest(const QString &code, const QString &input, const QString &language);
    void getTestResult(int judgeId);

    // 状态检查
    void checkStatus();

signals:
    void captchaFetched(const QString &cid, const QPixmap &image);
    void ocrResult(const QString &text);
    void loginResult(bool success, const QString &message);
    void submitResult(bool success, int judgeId, const QString &message);
    void testResultReady(const QString &result, const QString &output, const QString &error);
    void statusChecked(bool loggedIn, const QString &ocrEngine);
    void error(const QString &message);

private slots:
    void onCaptchaReply();
    void onOCRReply();
    void onLoginReply();
    void onSubmitReply();
    void onResultReply();
    void onStatusReply();

private:
    QString baseUrl;
    std::unique_ptr<QNetworkAccessManager> networkManager;
    QNetworkRequest createRequest(const QString &endpoint);
};

#endif // BACKEND_CLIENT_H
