import { useEffect, useRef, useState } from "react";

export default function MicTest() {
	const audioRef = useRef(null);
	const mediaRecorderRef = useRef(null);
	const chunksRef = useRef([]);

	const [permission, setPermission] = useState(false);
	const [recording, setRecording] = useState(false);
	const [audioURL, setAudioURL] = useState(null);
	const [volume, setVolume] = useState(0);

	// Request microphone permission on load
	useEffect(() => {
		navigator.mediaDevices
			.getUserMedia({ audio: true })
			.then(() => setPermission(true))
			.catch(() => setPermission(false));
	}, []);

	// Start Recording
	const startRecording = async () => {
		const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

		// Volume Analyzer
		const audioContext = new AudioContext();
		const source = audioContext.createMediaStreamSource(stream);
		const analyser = audioContext.createAnalyser();
		analyser.fftSize = 256;
		source.connect(analyser);

		const dataArray = new Uint8Array(analyser.frequencyBinCount);

		const detectVolume = () => {
			analyser.getByteFrequencyData(dataArray);
			const avgVolume = dataArray.reduce((a, b) => a + b) / dataArray.length;
			setVolume(avgVolume);
			if (recording) requestAnimationFrame(detectVolume);
		};
		detectVolume();

		mediaRecorderRef.current = new MediaRecorder(stream);
		chunksRef.current = [];

		mediaRecorderRef.current.ondataavailable = (e) => {
			chunksRef.current.push(e.data);
		};

		mediaRecorderRef.current.onstop = () => {
			const blob = new Blob(chunksRef.current, { type: "audio/wav" });
			const url = URL.createObjectURL(blob);
			setAudioURL(url);
		};

		mediaRecorderRef.current.start();
		setRecording(true);
	};

	// Stop Recording
	const stopRecording = () => {
		mediaRecorderRef.current.stop();
		setRecording(false);
	};

	return (
		<div style={{ padding: "30px", maxWidth: "600px", margin: "0 auto" }}>
			<h2>🎤 Microphone Test</h2>

			{!permission && (
				<p style={{ color: "red" }}>
					Microphone access is blocked! Enable it in browser settings.
				</p>
			)}

			{/* Volume Meter */}
			<div
				style={{
					width: "100%",
					height: "20px",
					background: "#ddd",
					borderRadius: "8px",
					marginTop: "15px",
					overflow: "hidden",
				}}
			>
				<div
					style={{
						width: `${volume}%`,
						height: "100%",
						background: volume < 10 ? "red" : "green",
						transition: "width 0.1s",
					}}
				></div>
			</div>

			<div style={{ marginTop: "20px" }}>
				{!recording ? (
					<button
						onClick={startRecording}
						style={{
							padding: "10px 20px",
							background: "blue",
							color: "white",
							borderRadius: "6px",
						}}
					>
						Start Mic Test
					</button>
				) : (
					<button
						onClick={stopRecording}
						style={{
							padding: "10px 20px",
							background: "red",
							color: "white",
							borderRadius: "6px",
						}}
					>
						Stop
					</button>
				)}
			</div>

			{audioURL && (
				<div style={{ marginTop: "20px" }}>
					<h4>Playback:</h4>
					<audio controls src={audioURL} ref={audioRef}></audio>
				</div>
			)}
		</div>
	);
}
