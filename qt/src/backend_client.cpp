#include "backend_client.h"
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QUrl>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QPixmap>
#include <QBuffer>
#include <QByteArray>

BackendClient::BackendClient(QObject *parent)
    : QObject(parent), baseUrl("http://127.0.0.1:5000") {
    networkManager = std::make_unique<QNetworkAccessManager>();
}

BackendClient::~BackendClient() = default;

QNetworkRequest BackendClient::createRequest(const QString &endpoint) {
    QUrl url(baseUrl + endpoint);
    QNetworkRequest request(url);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    return request;
}

void BackendClient::fetchLoginCaptcha() {
    QNetworkRequest request = createRequest("/api/captcha/login");
    QNetworkReply *reply = networkManager->get(request);

    connect(reply, &QNetworkReply::finished, this, &BackendClient::onCaptchaReply);
}

void BackendClient::fetchProblemCaptcha() {
    QNetworkRequest request = createRequest("/api/captcha/problem");
    QNetworkReply *reply = networkManager->get(request);

    connect(reply, &QNetworkReply::finished, this, &BackendClient::onCaptchaReply);
}

void BackendClient::performOCR(const QByteArray &imageData, const QString &mode) {
    QNetworkRequest request = createRequest("/api/ocr");

    QJsonObject json;
    json["image"] = QString::fromLatin1(imageData.toBase64());
    json["mode"] = mode;

    QJsonDocument doc(json);
    QNetworkReply *reply = networkManager->post(request, doc.toJson());

    connect(reply, &QNetworkReply::finished, this, &BackendClient::onOCRReply);
}

void BackendClient::login(const QString &username, const QString &password, const QString &code) {
    QNetworkRequest request = createRequest("/api/login");

    QJsonObject json;
    json["username"] = username;
    json["password"] = password;
    json["code"] = code;

    QJsonDocument doc(json);
    QNetworkReply *reply = networkManager->post(request, doc.toJson());

    connect(reply, &QNetworkReply::finished, this, &BackendClient::onLoginReply);
}

void BackendClient::submitTest(const QString &code, const QString &input, const QString &language) {
    QNetworkRequest request = createRequest("/api/submit/test");

    QJsonObject json;
    json["code"] = code;
    json["input"] = input;
    json["language"] = language;

    QJsonDocument doc(json);
    QNetworkReply *reply = networkManager->post(request, doc.toJson());

    connect(reply, &QNetworkReply::finished, this, &BackendClient::onSubmitReply);
}

void BackendClient::getTestResult(int judgeId) {
    QNetworkRequest request = createRequest(QString("/api/result/test/%1").arg(judgeId));
    QNetworkReply *reply = networkManager->get(request);

    connect(reply, &QNetworkReply::finished, this, &BackendClient::onResultReply);
}

void BackendClient::checkStatus() {
    QNetworkRequest request = createRequest("/api/status");
    QNetworkReply *reply = networkManager->get(request);

    connect(reply, &QNetworkReply::finished, this, &BackendClient::onStatusReply);
}

void BackendClient::onCaptchaReply() {
    QNetworkReply *reply = qobject_cast<QNetworkReply *>(sender());
    if (!reply) return;

    if (reply->error() == QNetworkReply::NoError) {
        QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
        QJsonObject obj = doc.object();

        if (obj["success"].toBool()) {
            QString cid = obj["cid"].toString();
            QString imageB64 = obj["image"].toString();

            QByteArray imageData = QByteArray::fromBase64(imageB64.toLatin1());
            QPixmap pixmap;
            pixmap.loadFromData(imageData);

            emit captchaFetched(cid, pixmap);
        }
    } else {
        emit error("Failed to fetch captcha: " + reply->errorString());
    }

    reply->deleteLater();
}

void BackendClient::onOCRReply() {
    QNetworkReply *reply = qobject_cast<QNetworkReply *>(sender());
    if (!reply) return;

    if (reply->error() == QNetworkReply::NoError) {
        QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
        QJsonObject obj = doc.object();

        if (obj["success"].toBool()) {
            emit ocrResult(obj["text"].toString());
        }
    } else {
        emit error("OCR failed: " + reply->errorString());
    }

    reply->deleteLater();
}

void BackendClient::onLoginReply() {
    QNetworkReply *reply = qobject_cast<QNetworkReply *>(sender());
    if (!reply) return;

    if (reply->error() == QNetworkReply::NoError) {
        QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
        QJsonObject obj = doc.object();

        bool success = obj["success"].toBool();
        emit loginResult(success, success ? "Login successful" : "Login failed");
    } else {
        emit loginResult(false, "Network error: " + reply->errorString());
    }

    reply->deleteLater();
}

void BackendClient::onSubmitReply() {
    QNetworkReply *reply = qobject_cast<QNetworkReply *>(sender());
    if (!reply) return;

    if (reply->error() == QNetworkReply::NoError) {
        QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
        QJsonObject obj = doc.object();

        if (obj["success"].toBool()) {
            int judgeId = obj["judge_id"].toInt();
            emit submitResult(true, judgeId, "Submit successful");
        } else {
            emit submitResult(false, -1, "Submit failed");
        }
    } else {
        emit submitResult(false, -1, "Network error: " + reply->errorString());
    }

    reply->deleteLater();
}

void BackendClient::onResultReply() {
    QNetworkReply *reply = qobject_cast<QNetworkReply *>(sender());
    if (!reply) return;

    if (reply->error() == QNetworkReply::NoError) {
        QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
        QJsonObject obj = doc.object();

        if (obj["success"].toBool()) {
            QJsonObject data = obj["data"].toObject();
            emit testResultReady(
                data["result"].toString(),
                data["output"].toString(),
                data["compile_error"].toString()
            );
        }
    } else {
        emit error("Failed to get result: " + reply->errorString());
    }

    reply->deleteLater();
}

void BackendClient::onStatusReply() {
    QNetworkReply *reply = qobject_cast<QNetworkReply *>(sender());
    if (!reply) return;

    if (reply->error() == QNetworkReply::NoError) {
        QJsonDocument doc = QJsonDocument::fromJson(reply->readAll());
        QJsonObject obj = doc.object();

        if (obj["success"].toBool()) {
            emit statusChecked(obj["logged_in"].toBool(), obj["ocr_engine"].toString());
        }
    }

    reply->deleteLater();
}
