$(function () {
  $('[data-toggle="tooltip"]').tooltip()
});

function upload2S3(video_id) {
    console.log(video_id)
    $("#loading-text-message").html("Please wait while downloading video...")
    $("#inprogress").css('display', 'block');
    $("#loading-text-message").html("Loading...");
    fetch(`/channel/video/s3upload?video_id=${video_id}`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({"video_id": video_id})
    }).then((response) => {
        $("#inprogress").css('display', 'none');
        $("#loading-text-message").html("");
        return response.json();
    }).then((response) => {
        let message = "Failed to upload at S3";
        if (response?.isUploaded) {
            message = "Uploaded successfully!"
        }
        alert(message);
    });
}
