<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = $_POST["name"];
    $email = $_POST["email"];
    $message = $_POST["message"];

    // Replace with your actual email address
    $to = "justinevaughnr@outlook.com";
    $subject = "New Contact Form Submission";

    $headers = "From: $email" . "\r\n" .
               "Reply-To: $email" . "\r\n" .
               "X-Mailer: PHP/" . phpversion();

    $mailBody = "Name: $name\nEmail: $email\n\n$message";

    // Use mail() function to send the email
    mail($to, $subject, $mailBody, $headers);

    // Redirect after sending the email (you might want to customize this URL)
    header("Location: thank-you.html");
    exit;
}
?>
